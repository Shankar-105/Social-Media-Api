# redis_service.py
# A simple Redis caching helper for our FastAPI project.
#
# WHAT IS REDIS?
#   Redis is an in-memory key-value store. Think of it like a super-fast
#   Python dictionary that lives outside your app.  Because the data sits
#   in RAM (not on disk like PostgreSQL), reads/writes are *extremely* fast
#   — perfect for caching responses so we don't hit the database every time.
#
# HOW THIS MODULE WORKS (step by step):
#   1. We create ONE shared Redis connection when the app starts.
#   2. Before hitting the DB, a route checks Redis: "do I already have
#      this data cached?"  If YES → return the cached JSON instantly.
#   3. If NO → query the DB as usual, then STORE the result in Redis
#      with an expiration time (TTL). Next request gets the cached copy.
#   4. When data changes (create / update / delete), we INVALIDATE
#      (delete) the relevant cache keys so stale data is never served.

import redis
import json
from typing import Any, Optional
from app.config import settings

# ──────────────── 1. CREATE THE REDIS CLIENT ────────────────
# This is similar to how db.py creates the SQLAlchemy engine.
# We make ONE client object and import it wherever we need caching.
#   host  = where your Redis server is running  (localhost / WSL)
#   port  = default Redis port 6379
#   db    = Redis has 16 databases (0-15), we use 0
#   decode_responses=True  →  gives us normal Python strings
#                              instead of raw bytes (b"hello")

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True       # ← very important for convenience
)


# HELPER FUNCTION

def ping_redis() -> bool:
    """
    Check if Redis is reachable.
    Returns True if connected, False otherwise.
    
    Under the hood this sends the PING command to the Redis server,
    and Redis replies with PONG.
    """
    try:
        return redis_client.ping()   # → True
    except redis.ConnectionError:
        return False

# STARTUP CHECK 

def check_redis_connection() -> None:
    """
    Call this once at app startup to confirm Redis is reachable.
    Prints a clear message to your terminal.
    """
    if ping_redis():
        print("✅ Redis connection successful!")
    else:
        print("❌ Redis connection FAILED — caching will not work.")
        print(f"   Tried connecting to {settings.redis_host}:{settings.redis_port}")
        print("   Make sure your Redis server is running (e.g. in WSL: sudo service redis-server start)")
