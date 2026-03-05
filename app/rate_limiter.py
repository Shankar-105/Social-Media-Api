"""
app/rate_limiter.py
===================
Fixed Window rate limiting using Redis INCR + EXPIRE.

Two public factory functions:

  ip_rate_limit(endpoint_id, max_calls, window)
      Returns a FastAPI Depends-compatible dependency keyed by client IP.
      Use for unauthenticated routes: login, signup, forgot-password, reset-password.

  user_rate_limit(endpoint_id, max_calls, window)
      Returns a FastAPI Depends-compatible dependency keyed by authenticated user ID.
      Use for authenticated write routes: comment, create-post, follow, change-password.

Both factories return a coroutine that FastAPI resolves as a Depends dependency.
If the requester is within the limit  → dependency returns None silently.
If the requester is over the limit    → HTTP 429 raised with Retry-After header.

Redis is accessed via the module reference (_redis_svc.redis_client) so that
conftest.py's fakeredis patch is respected during tests.  A direct
  from app.redis_service import redis_client
would capture the real aioredis object at import time and ignore the patch.
Accessing _redis_svc.redis_client is a live attribute lookup — always reads
the current value, including any test-time override.
"""

from fastapi import Depends, HTTPException, Request, status
from app import models, oauth2
from app import redis_service as _redis_svc


async def _check(key: str, max_calls: int, window: int) -> None:
    """
    Core fixed window enforcement.

    INCR atomically creates-or-increments the Redis key and returns the new count.
    On the very first request of a new window (count == 1) we arm the TTL so the
    key auto-deletes when the window expires.  If the count exceeds max_calls we
    read the remaining TTL and raise HTTP 429 with a Retry-After header telling
    the client exactly how many seconds to wait.

    The two-command sequence (INCR then conditional EXPIRE) has a tiny theoretical
    race: two simultaneous first-requests could both see count==1 and both call
    EXPIRE.  That is harmless — Redis EXPIRE is idempotent and both calls would
    set the same TTL — and the race only ever occurs on the very first hit of
    each new window.
    """
    count = await _redis_svc.redis_client.incr(key)
    if count == 1:
        # First hit in this window — start the expiry clock
        await _redis_svc.redis_client.expire(key, window)

    if count > max_calls:
        ttl = await _redis_svc.redis_client.ttl(key)
        retry_after = max(ttl, 1)   # guard against 0 if key just expired
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {retry_after}s.",
            headers={"Retry-After": str(retry_after)},
        )


def ip_rate_limit(endpoint_id: str, max_calls: int, window: int):
    """
    Factory → returns a FastAPI dependency keyed by client IP address.

    Redis key format : "rl:<endpoint_id>:ip:<ip>"
    Example          : "rl:login:ip:203.0.113.5"

    FastAPI injects Request automatically into the returned inner coroutine;
    no changes to the calling route's own signature are needed beyond adding
    a `_: None = Depends(ip_rate_limit(...))` parameter.

    Parameters
    ----------
    endpoint_id : unique label for this limit — keeps keys from colliding across endpoints
    max_calls   : how many requests an IP may make per window
    window      : window length in seconds (e.g. 300 = 5 minutes)
    """
    async def dependency(request: Request) -> None:
        ip = request.client.host if request.client else "unknown"
        key = f"rl:{endpoint_id}:ip:{ip}"
        await _check(key, max_calls, window)

    return dependency


def user_rate_limit(endpoint_id: str, max_calls: int, window: int):
    """
    Factory → returns a FastAPI dependency keyed by authenticated user ID.

    Redis key format : "rl:<endpoint_id>:user:<user_id>"
    Example          : "rl:comment:user:42"

    The returned dependency calls Depends(oauth2.getCurrentUser) internally.
    FastAPI caches every Depends result within a single request — so if the
    route itself also depends on getCurrentUser, the JWT is decoded exactly
    once, not twice.

    Parameters
    ----------
    endpoint_id : unique label for this limit
    max_calls   : how many requests a user may make per window
    window      : window length in seconds
    """
    async def dependency(current_user: models.User = Depends(oauth2.getCurrentUser)) -> None:
        key = f"rl:{endpoint_id}:user:{current_user.id}"
        await _check(key, max_calls, window)

    return dependency
