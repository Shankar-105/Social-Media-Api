# Async Migration Changelog

This document tracks every change made during the async migration of the FastAPI codebase.  
Each phase is documented with **what changed**, **why**, and **where**.

---

## Phase 1 — Foundation (Dependencies + DB Engine + Redis Client)

> **Goal:** Swap the underlying drivers and core infrastructure to async so every layer above can `await`.

### 1. `requirements.txt` — New dependencies added

| Package | Why |
|---------|-----|
| `asyncpg` | Async PostgreSQL driver — replaces `psycopg2-binary` at runtime. SQLAlchemy's `create_async_engine` talks to Postgres through this. |
| `aiofiles` | Async file I/O — needed in later phases for media uploads (`open()`, `shutil.copyfileobj` → `aiofiles.open()`). Added now so it's available. |

- `psycopg2-binary` is **kept** — Alembic still needs it for sync migrations.
- `redis==7.0.1` already bundles `redis.asyncio` — no new package needed.

### 2. `app/db.py` — Async engine + session, sync engine preserved

**Before:** One sync engine, one sync `sessionmaker`, one sync `getDb()` generator.

**After:**

| Symbol | What it is | Used by |
|--------|-----------|---------|
| `ASYNC_SQL_ALCHEMY_URL` | `postgresql+asyncpg://...` connection string | `async_engine` |
| `async_engine` | `create_async_engine(...)` | The runtime async DB engine |
| `AsyncSessionLocal` | `async_sessionmaker(AsyncSession)` | All route/service DB sessions |
| `async def getDb()` | Async generator yielding `AsyncSession` | Every `Depends(getDb)` across the app |
| `SYNC_SQL_ALCHEMY_URL` | `postgresql://...` (psycopg2) connection string | Alembic + `create_all` |
| `sync_engine` | `create_engine(...)` | `main.py` table creation + Alembic |
| `Base` | `declarative_base()` — unchanged | Models |

- The old `SQL_ALCHEMY_URL` is renamed to `SYNC_SQL_ALCHEMY_URL` so Alembic's import still resolves (Alembic env.py updated to match).
- `engine` is renamed to `sync_engine` for clarity.

### 3. `app/redis_service.py` — Fully async Redis client

**Before:** Every function was sync using `redis.Redis(...)`.

**After:** 

- Client changed from `redis.Redis(...)` → `redis.asyncio.Redis(...)`.
- All 8 functions converted to `async def` with `await` on every Redis call:
  - `ping_redis()` → `await redis_client.ping()`
  - `set_cache()` → `await redis_client.setex(...)`
  - `get_cache()` → `await redis_client.get(...)`
  - `delete_cache()` → `await redis_client.delete(...)`
  - `delete_cache_pattern()` → async `scan` loop with `await`
  - `check_redis_connection()` → `await ping_redis()`
  - `add_to_blacklist()` → `await redis_client.setex(...)`
  - `is_blacklisted()` → `await redis_client.exists(...)`

Every caller of these functions (routes, oauth2, etc.) will need `await` — handled in later phases.

### 4. `app/main.py` — Startup adjusted

- Import changed: `from app.db import engine` → `from app.db import sync_engine`
- `create_all` now uses `sync_engine` (sync driver for table creation).
- `startup_event()` converted to `async def` so it can `await check_redis_connection()`.

### 5. `alembic/env.py` — Import updated

- `from app.db import SQL_ALCHEMY_URL` → `from app.db import SYNC_SQL_ALCHEMY_URL`
- `config.set_main_option('sqlalchemy.url', SQL_ALCHEMY_URL)` → `config.set_main_option('sqlalchemy.url', SYNC_SQL_ALCHEMY_URL)`
- Everything else stays sync — Alembic runs as a CLI tool, not during request handling.

---

## Phase 2 — Auth Middleware + Services (the chokepoint)

> **Goal:** Convert the authentication layer (`oauth2.py`) and supporting services (`otp_service.py`, `utils.py`) to async. This is the chokepoint — every protected route depends on `getCurrentUser`, which depends on `verifyAccesstoken`, which hits both Redis and the DB. Until this is async, nothing downstream can be.

### 1. `app/oauth2.py` — Fully async token verification + user resolution

**What changed:**

| Function | Before | After |
|----------|--------|-------|
| `createAccessToken(data)` | `def` (sync) | **No change** — pure CPU (JWT encode), no I/O |
| `verifyAccesstoken(token, cred_exc, dbs)` | `def`, `Session`, `dbs.query(...)`, sync `redis_service.is_blacklisted()` | `async def`, `AsyncSession`, `await dbs.execute(select(...))`, `await redis_service.is_blacklisted()` |
| `getCurrentUser(token, dbs)` | `def`, `Session` from `Depends(db.getDb)` | `async def`, `AsyncSession` from `Depends(db.getDb)`, `return await verifyAccesstoken(...)` |

**Key import changes:**
- `from sqlalchemy.orm import Session` → `from sqlalchemy.ext.asyncio import AsyncSession`
- Added `from sqlalchemy import select`

**DB query pattern change:**
```python
# BEFORE (sync)
user = dbs.query(models.User).filter(models.User.id == id).first()

# AFTER (async)
result = await dbs.execute(select(models.User).where(models.User.id == id))
user = result.scalars().first()
```

**Redis call change:**
```python
# BEFORE (sync)
if redis_service.is_blacklisted(token):

# AFTER (async)
if await redis_service.is_blacklisted(token):
```

### 2. `app/otp_service.py` — Async OTP save + check

**What changed:**

| Function | Before | After |
|----------|--------|-------|
| `generateOtp()` | `def` (sync) | **No change** — pure CPU (`random.randint`) |
| `saveOtp(db, email, otp)` | `def`, `Session`, `.query().delete()`, `.add()`, `.commit()`, `.refresh()` | `async def`, `AsyncSession`, `await db.execute(delete(...))`, `.add()`, `await db.commit()`, `await db.refresh()` |
| `checkOtp(db, email, user_otp)` | `def`, `Session`, `.query().first()`, `db.delete()`, `.commit()` | `async def`, `AsyncSession`, `await db.execute(select(...))` + `.scalars().first()`, `await db.delete()`, `await db.commit()` |

**Key import changes:**
- `from sqlalchemy.orm import Session` → `from sqlalchemy.ext.asyncio import AsyncSession`
- Added `from sqlalchemy import select, delete`

**DB query pattern change:**
```python
# BEFORE — bulk delete
db.query(models.OTP).filter(models.OTP.email == email).delete()

# AFTER — async delete statement
await db.execute(delete(models.OTP).where(models.OTP.email == email))
```

### 3. `app/my_utils/utils.py` — Async OTP cleanup

**What changed:**

| Function | Before | After |
|----------|--------|-------|
| `hashPassword(password)` | `def` (sync) | **No change** — CPU-bound bcrypt, staying sync per decision |
| `verifyPassword(plain, hashed)` | `def` (sync) | **No change** — same reasoning |
| `cleanUpExpiredOtps(db)` | `def`, `Session`, `.query().delete()`, `.commit()` | `async def`, `AsyncSession`, `await db.execute(delete(...))`, `await db.commit()` |

**Key import changes:**
- `from sqlalchemy.orm import Session` → `from sqlalchemy.ext.asyncio import AsyncSession`
- Added `from sqlalchemy import select, delete`

### Why this phase matters

`getCurrentUser` is injected via `Depends()` into **every single protected route** in the app. Now that it's `async def` returning an awaited result from an `AsyncSession`, all downstream routes that depend on it will seamlessly receive the resolved `User` object. Without this phase, no route could be converted to async.

---

## Why Tests Fail After Phase 1 & 2 (and why that's expected)

### The Error You See

```
RuntimeWarning: coroutine 'getCurrentUser' was never awaited
RuntimeWarning: coroutine 'delete_cache' was never awaited
starlette.websockets.WebSocketDisconnect
```

### What's Happening — The Half-Async Problem

We're in a **transitional state**. Here's the situation:

| Layer | Status after Phase 2 | Status needed |
|-------|---------------------|---------------|
| `db.py` — `getDb()` | ✅ Async (yields `AsyncSession`) | — |
| `redis_service.py` — all functions | ✅ Async | — |
| `oauth2.py` — `getCurrentUser()` | ✅ Async | — |
| `otp_service.py` — `saveOtp`, `checkOtp` | ✅ Async | — |
| **Route files** (`users.py`, `auth.py`, etc.) | ❌ **Still sync `def`** | Need `async def` |
| **Tests** (`conftest.py`) | ❌ **Still sync, overrides with sync Session** | Need async override |

The route endpoints (like `createUser`, `loginUser`, the WebSocket handler) are still declared as **`def`** (sync), but they now receive dependencies that are **`async def`** (like `getCurrentUser`, `getDb`, `delete_cache`).

**Here's the core problem:**

When a **sync `def` route** calls an **`async def` dependency**, FastAPI handles `Depends()` correctly (it awaits async deps even for sync routes). BUT inside the route body, if you call an async function like `delete_cache("all_users")` without `await`, Python creates a **coroutine object and throws it away**. The function never actually runs.

Example from `users.py` line 74:
```python
def createUser(...):           # ← sync route
    ...
    delete_cache("all_users")  # ← this is NOW async, but no 'await' → silently does NOTHING
    return newUser
```

The WebSocket test fails because `getCurrentUser` is now `async def`, but the chat WebSocket handler calls into code paths that don't properly `await` it — the coroutine is created but never executed, so the user is never authenticated, and the WebSocket closes with code 1008.

### Why the Tests Will Work Again

Once **Phase 3** (route files) and **Phase 5** (chat system) are converted, every route will be `async def` and will `await` all async dependencies. Then the only remaining issue is...

### The Test-Specific Problem (conftest.py)

Even after all routes are async, the **tests** will still fail because of `conftest.py`:

```python
# conftest.py currently does this:
def override_getDb():          # ← SYNC generator
    db = TestingSessionLocal() # ← SYNC session (psycopg2)
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[getDb] = override_getDb  # ← overrides async getDb with sync version
```

The app's `getDb` now yields an `AsyncSession`, but the test override yields a **sync `Session`**. When routes do `await db.execute(select(...))`, they'll crash because a sync `Session` doesn't support `await`.

**This will be fixed when we convert the test suite** (deferred to after all application phases are done). The fix is straightforward: use an async test engine + `AsyncSession` in conftest.

---

## Deep Dive: Why We Can't "Just Add async/await to Routes"

> "Can't we just change all routes to `async def` and `await` the DB calls? Why do we need `asyncpg`, new engines, `AsyncSession`, etc.?"

Great question. Here's why it's not that simple:

### How SQLAlchemy Talks to PostgreSQL

```
Your Python code
    ↓
SQLAlchemy ORM  (translates Python objects → SQL queries)
    ↓
SQLAlchemy Engine  (manages connection pool, sends raw SQL)
    ↓
Database Driver  (the actual library that opens a TCP socket to PostgreSQL)
    ↓
PostgreSQL Server
```

The **driver** is the bottom layer — the one that actually sends bytes over the network and waits for PostgreSQL to respond. Everything above depends on it.

### The Problem with `psycopg2` (the old driver)

`psycopg2` is a **synchronous/blocking** driver. When it sends a query to PostgreSQL, it does this:

```
1. Send SQL query over TCP socket
2. BLOCK the entire thread until PostgreSQL responds  ← THIS IS THE PROBLEM
3. Return the result
```

Even if you write `async def` and `await`, the actual network I/O is happening inside `psycopg2`, and **it blocks**. Python's `await` can only yield control back to the event loop if the underlying I/O operation is itself async. `psycopg2` doesn't know what an event loop is — it just blocks.

So this would happen:
```python
async def get_user(db):
    # You THINK this is non-blocking because of 'await'...
    result = await db.execute(select(User).where(User.id == 1))
    # ...but psycopg2 underneath BLOCKS the entire event loop
    # while waiting for PostgreSQL to respond.
    # Every other request is frozen during this time.
```

**Result:** Your app looks async but behaves 100% synchronously. You get zero benefit. In fact it's *worse* because you added overhead with no gain.

### What `asyncpg` Does

`asyncpg` is a **natively async** PostgreSQL driver. It uses Python's `asyncio` event loop directly:

```
1. Send SQL query over TCP socket
2. Tell the event loop: "I'm waiting for data, go handle other requests"  ← NON-BLOCKING
3. Event loop serves other requests while PostgreSQL is thinking
4. PostgreSQL responds → event loop wakes up this coroutine
5. Return the result
```

This is **true async I/O**. While one request waits for its database query, the event loop can handle hundreds of other requests.

### Why We Need `create_async_engine` and `AsyncSession`

SQLAlchemy needs to know it's working with an async driver. That's why:

| Old (sync) | New (async) | Why |
|-----------|------------|-----|
| `create_engine(url)` | `create_async_engine(url)` | Tells SQLAlchemy to use async connection pooling and async I/O |
| `sessionmaker(...)` returning `Session` | `async_sessionmaker(...)` returning `AsyncSession` | `Session.execute()` is sync (blocks). `AsyncSession.execute()` is a coroutine (can be awaited). |
| `postgresql://` (URL scheme) | `postgresql+asyncpg://` | The `+asyncpg` tells SQLAlchemy to load the `asyncpg` driver instead of `psycopg2` |
| `def getDb(): yield db` | `async def getDb(): yield db` | FastAPI needs an async generator to properly manage the session lifecycle in async context |

### The Full Stack, Visualized

```
BEFORE (everything blocks):
──────────────────────────────────────────────
Request 1 → def route() → Session.query() → psycopg2 [BLOCKS 50ms]
Request 2 →                                   (waiting...)
Request 3 →                                   (waiting...)
              Total time: 150ms (sequential)

AFTER (true async):
──────────────────────────────────────────────
Request 1 → async def route() → await AsyncSession.execute() → asyncpg [non-blocking]
Request 2 → async def route() → await AsyncSession.execute() → asyncpg [non-blocking]
Request 3 → async def route() → await AsyncSession.execute() → asyncpg [non-blocking]
              Total time: ~50ms (concurrent)
```

### Same Logic for Redis

The same principle applies to Redis:

| Old | New | Why |
|-----|-----|-----|
| `redis.Redis(...)` | `redis.asyncio.Redis(...)` | `redis.Redis.get()` blocks the thread. `redis.asyncio.Redis.get()` is a coroutine — non-blocking. |

### Same Logic for File I/O (`aiofiles`)

| Old | New | Why |
|-----|-----|-----|
| `open("file", "wb")` | `aiofiles.open("file", "wb")` | `open()` blocks the thread while writing to disk. `aiofiles.open()` offloads to a thread pool so the event loop isn't blocked. |

### TL;DR

You can't just slap `async`/`await` on top of sync code. The **entire I/O stack** must be async from top to bottom:

```
async def route()        ← Layer 1: Route declaration
    ↓ await
AsyncSession.execute()   ← Layer 2: SQLAlchemy async session
    ↓ await
asyncpg                  ← Layer 3: Async database driver (THE KEY PIECE)
    ↓ non-blocking I/O
PostgreSQL               ← Layer 4: Database server
```

If **any** layer in this stack is synchronous, it blocks the event loop and nullifies all the async above it. `asyncpg` is the foundation that makes everything above it actually non-blocking.

---

## Phase 3 — Route Files Batch 1 (auth, posts, users, like, connect)

> **Goal:** Convert the first batch of route files to fully async endpoints. Every `def` → `async def`, every `Session` → `AsyncSession`, every `db.query()` → `await db.execute(select(...))`, and every sync Redis/file I/O call → `await`.

### Prerequisite: `app/models.py` — `lazy="selectin"` on ALL relationships

Before touching any route, we added **`lazy="selectin"`** to every single relationship in `models.py`. This is critical.

**Why:** In async SQLAlchemy, accessing a lazy-loaded relationship (the default `lazy="select"`) triggers a **synchronous SQL query behind the scenes**. Under `AsyncSession`, this causes a `MissingGreenlet` error because SQLAlchemy tries to do sync I/O inside an async context.

`lazy="selectin"` tells SQLAlchemy to eagerly load relationships using a `SELECT ... IN (...)` query at the time the parent object is loaded. The relationship data is already in memory when you access it — no surprise SQL, no `MissingGreenlet`.

**What changed:**

- Added `from sqlalchemy.orm import relationship, backref` (added `backref` import)
- Every `relationship(...)` and `backref=...` now includes `lazy="selectin"`
- For named backrefs, changed from `backref="name"` → `backref=backref("name", lazy="selectin")`

**Affected relationships (all 16):**

| Model | Relationship | Change |
|-------|-------------|--------|
| `User` | `posts` | Added `lazy="selectin"` |
| `User` | `followers` + backref `following` | Both sides `lazy="selectin"` |
| `User` | `voted_posts` | Added `lazy="selectin"` |
| `User` | `total_comments` | Added `lazy="selectin"` |
| `Post` | `shared_posts` | Added `lazy="selectin"` |
| `SharedPost` | `user` | Added `lazy="selectin"` |
| `SharedPost` | `post` | Added `lazy="selectin"` |
| `Message` | `sender_rel` + backref | Both `lazy="selectin"` |
| `Message` | `receiver_rel` + backref | Both `lazy="selectin"` |
| `MessageReaction` | `user` | Added `lazy="selectin"` |
| `SharedPostReaction` | `user` | Added `lazy="selectin"` |
| `DeletedSharedPost` | `user` | Added `lazy="selectin"` |
| `DeletedSharedPost` | `shared_post` | Added `lazy="selectin"` |
| `MessageReplies` | `sender_rel` + backref | Both `lazy="selectin"` |
| `MessageReplies` | `receiver_rel` + backref | Both `lazy="selectin"` |
| `SharedPostReplies` | `sender_rel` + backref | Both `lazy="selectin"` |

---

### 1. `app/routes/auth.py` — 4 async endpoints

**Endpoints converted:** `loginUser`, `logout`, `forgot_password`, `reset_password`

**Import changes:**
- `from sqlalchemy.orm import Session` → `from sqlalchemy.ext.asyncio import AsyncSession`
- Added `from sqlalchemy import select`
- Fixed duplicate imports: removed `import datetime` (conflicts with `from datetime import datetime`), removed duplicate `redis_service` import
- Added missing `from app import otp_service` import

**DB query pattern changes:**
```python
# BEFORE
user = db.query(models.User).filter(models.User.email == userCreds.username).first()

# AFTER
result = await db.execute(select(models.User).where(models.User.email == userCreds.username))
user = result.scalars().first()
```

**Async call changes:**
```python
# BEFORE (sync calls to now-async functions)
redis_service.add_to_blacklist(token, remaining_time)
otp_service.saveOtp(db, email, otp)
otp_service.checkOtp(db, request.email, request.otp)

# AFTER
await redis_service.add_to_blacklist(token, remaining_time)
await otp_service.saveOtp(db, email, otp)
await otp_service.checkOtp(db, request.email, request.otp)
```

---

### 2. `app/routes/posts.py` — 4 async endpoints

**Endpoints converted:** `getPost`, `create_post`, `deletePost`, `editPost`

**Import changes:**
- `from sqlalchemy.orm import Session` → `from sqlalchemy.ext.asyncio import AsyncSession`
- Added `from sqlalchemy import select`
- Added `import aiofiles` and `import asyncio`
- Removed `import shutil`

**File I/O migration (create_post):**
```python
# BEFORE (sync, blocking)
import shutil
with open(media_path, "wb") as buffer:
    shutil.copyfileobj(media.file, buffer)

# AFTER (async, non-blocking)
import aiofiles
content_bytes = await media.read()
async with aiofiles.open(media_path, "wb") as buffer:
    await buffer.write(content_bytes)
```

**File deletion (deletePost, editPost):**
```python
# BEFORE (sync)
os.remove(media_path)

# AFTER (offloaded to thread pool)
await asyncio.to_thread(os.remove, media_path)
```

**DB pattern — all standard conversions:**
- `db.query(M).filter(...).first()` → `(await db.execute(select(M).where(...))).scalars().first()`
- `db.add()` / `await db.commit()` / `await db.refresh()`
- `await db.delete(obj)` / `await db.commit()`

---

### 3. `app/routes/users.py` — 7 async endpoints

**Endpoints converted:** `createUser`, `getUserById`, `getUserProfileById`, `getUserPostsById`, `getUserFollowers`, `getUserFollowing`, `deleteUser`

**Import changes:**
- `from sqlalchemy.orm import Session` → `from sqlalchemy.ext.asyncio import AsyncSession`
- Added `from sqlalchemy import select, func`
- Added `import asyncio`

**Redis cache calls — all now `await`ed:**
```python
# BEFORE
cached = redis_service.get_cache("all_users")
redis_service.set_cache("all_users", response_data)
redis_service.delete_cache("all_users")
redis_service.delete_cache_pattern("user_profile_*")

# AFTER
cached = await redis_service.get_cache("all_users")
await redis_service.set_cache("all_users", response_data)
await redis_service.delete_cache("all_users")
await redis_service.delete_cache_pattern("user_profile_*")
```

**Performance optimization — `len(user.posts)` → count query:**
```python
# BEFORE (loads ALL posts into memory just to count them)
post_count = len(user.posts)

# AFTER (efficient SQL COUNT)
post_count_result = await db.execute(
    select(func.count()).select_from(models.Post).where(models.Post.owner_id == user.id)
)
post_count = post_count_result.scalar()
```

**Variable name fix:** Renamed `result` → `result_response` for the `UserProfileResponse` dict to avoid shadowing the SQLAlchemy `result` variable.

---

### 4. `app/routes/like.py` — 2 async endpoints

**Endpoints converted:** `likePost`, `getLikes`

**Key change — error handling:**
```python
# BEFORE (sync rollback)
except IntegrityError:
    db.rollback()

# AFTER (async rollback)
except IntegrityError:
    await db.rollback()
```

Standard `db.query()` → `await db.execute(select(...))` conversions throughout.

---

### 5. `app/routes/connect.py` — 5 async endpoints (MOST COMPLEX)

**Endpoints converted:** `follow_user`, `unfollow_user`, `remove_follower`, `get_followers`, `get_following`

**This file required a complete rewrite**, not just adding `async`/`await`.

**The Problem:** The original sync code used SQLAlchemy relationship methods on the many-to-many `connections` table:

```python
# BEFORE — append/remove on relationship collections
current_user.following.append(target_user)   # triggers sync INSERT
current_user.following.remove(target_user)   # triggers sync DELETE
target_user in current_user.following        # triggers lazy load
```

Under `AsyncSession`, these operations trigger **synchronous SQL behind the scenes**, causing `MissingGreenlet` errors. Even `lazy="selectin"` doesn't help here because `.append()` and `.remove()` perform **write operations** that go through SQLAlchemy's sync internals.

**The Solution:** Direct SQL operations on the `connections` association table:

```python
from sqlalchemy import insert, delete, select, func
from app.models import connections  # the Table object, not an ORM model

# FOLLOW — direct INSERT
await db.execute(
    insert(connections).values(followed_id=target_user.id, follower_id=current_user.id)
)
await db.commit()

# UNFOLLOW — direct DELETE
await db.execute(
    delete(connections).where(
        (connections.c.followed_id == target_user.id) &
        (connections.c.follower_id == current_user.id)
    )
)
await db.commit()

# CHECK IF FOLLOWING — direct SELECT
existing = await db.execute(
    select(connections).where(
        (connections.c.followed_id == target_user.id) &
        (connections.c.follower_id == current_user.id)
    )
)
already_following = existing.first() is not None

# COUNT followers/following
count_result = await db.execute(
    select(func.count()).select_from(connections).where(
        connections.c.followed_id == user_id
    )
)
follower_count = count_result.scalar()
```

**get_followers / get_following — complete rewrite:**

The original code accessed `user.followers` / `user.following` relationships and iterated over User objects. The async version uses explicit JOINs:

```python
# Get followers with pagination
followers_result = await db.execute(
    select(models.User)
    .join(connections, connections.c.follower_id == models.User.id)
    .where(connections.c.followed_id == user.id)
    .offset(skip).limit(limit)
)
followers = followers_result.scalars().all()

# For is_following check — get IDs the current user follows
following_result = await db.execute(
    select(connections.c.followed_id).where(connections.c.follower_id == current_user.id)
)
current_following_ids = {row[0] for row in following_result.fetchall()}
```

---

## Phase 4 — Route Files Batch 2 (comment, search, me, changepassword, feed)

> **Goal:** Convert the remaining 5 route files to fully async. This completes the async migration of all API routes.

### 1. `app/routes/comment.py` — 4 async endpoints

**Endpoints converted:** `create_comment`, `get_comments`, `delete_comment`, `edit_comment`

**Standard conversions:**
- All `def` → `async def`
- `Session` → `AsyncSession`
- `db.query()` → `await db.execute(select(...))`
- `db.commit()` → `await db.commit()`
- `db.refresh()` → `await db.refresh()`
- `db.delete()` → `await db.delete()`

**Relationship access works thanks to Phase 3 prerequisite:** `comment.user` (for serializing commenter info) works without extra queries because `lazy="selectin"` eagerly loads the user when the comment is fetched.

---

### 2. `app/routes/search.py` — 1 async endpoint

**Endpoint converted:** `search`

**Complex query rewrite:**

```python
# BEFORE — chained sync query with .ilike()
query = db.query(models.User).filter(
    or_(
        models.User.username.ilike(f"%{search_query}%"),
        models.User.email.ilike(f"%{search_query}%")
    )
)
total = query.count()
users = query.offset(skip).limit(limit).all()

# AFTER — separate count + data queries
base_filter = or_(
    models.User.username.ilike(f"%{search_query}%"),
    models.User.email.ilike(f"%{search_query}%")
)
count_result = await db.execute(
    select(func.count()).select_from(models.User).where(base_filter)
)
total = count_result.scalar()
users_result = await db.execute(
    select(models.User).where(base_filter).offset(skip).limit(limit)
)
users = users_result.scalars().all()
```

**Why two queries?** In sync SQLAlchemy you could call `.count()` on a query object, then reuse it for `.all()`. In async, `await db.execute()` consumes the result — you can't reuse it. Separating the count and data queries is the clean async pattern.

---

### 3. `app/routes/me.py` — 11 async endpoints (LARGEST FILE)

**Endpoints converted:** `getMyProfile`, `getMyAnalytics`, `getMyPosts`, `getMyFollowers`, `getMyFollowing`, `getMyVotedPosts`, `getMyComments`, `editProfile`, `editProfilePicture`, `changePassword`, `deleteProfile`

**Import changes:**
- `from sqlalchemy.orm import Session` → `from sqlalchemy.ext.asyncio import AsyncSession`
- Added `from sqlalchemy import select, func, update`
- Added `import aiofiles` and `import asyncio`
- Removed `import shutil`

**Performance optimizations — len() → COUNT queries:**
```python
# BEFORE (loads ALL posts/comments into memory to count)
post_count = len(currentUser.posts)
comment_count = len(currentUser.total_comments)

# AFTER (efficient SQL COUNT — just returns a number)
post_count = (await db.execute(
    select(func.count()).select_from(models.Post).where(models.Post.owner_id == currentUser.id)
)).scalar()
comment_count = (await db.execute(
    select(func.count()).select_from(models.Comment).where(models.Comment.user_id == currentUser.id)
)).scalar()
```

**Voted posts — relationship access → explicit JOIN:**
```python
# BEFORE (accesses relationship which loads all Vote objects + related Posts)
voted_posts = currentUser.voted_posts

# AFTER (explicit query with JOIN)
voted_result = await db.execute(
    select(models.Post)
    .join(models.Vote, models.Vote.post_id == models.Post.id)
    .where(models.Vote.user_id == currentUser.id)
    .offset(skip).limit(limit)
)
voted_posts = voted_result.scalars().all()
```

**Update pattern:**
```python
# BEFORE
db.query(models.User).filter(models.User.id == currentUser.id).update(update_data)
db.commit()

# AFTER
await db.execute(update(models.User).where(models.User.id == currentUser.id).values(**update_data))
await db.commit()
```

**File I/O — profile picture upload:**
```python
# BEFORE (sync)
with open(file_path, "wb") as buffer:
    shutil.copyfileobj(profilePic.file, buffer)

# AFTER (async)
content_bytes = await profilePic.read()
async with aiofiles.open(file_path, "wb") as buffer:
    await buffer.write(content_bytes)
```

**File deletion:**
```python
# BEFORE
os.remove(old_pic_path)

# AFTER
await asyncio.to_thread(os.remove, old_pic_path)
```

---

### 4. `app/routes/changepassword.py` — 2 endpoints + 1 helper

**Endpoints converted:** `change_password_request`, `change_password_verify`  
**Helper converted:** `verifyOtp()` → `async def verifyOtp()`

**Key changes:**
```python
# Helper function
async def verifyOtp(db: AsyncSession, email, otp):
    return await otp_service.checkOtp(db, email, otp)

# OTP operations
await otp_service.saveOtp(db, user.email, otp)
is_valid = await verifyOtp(db, user.email, request.otp)
```

Standard DB query conversions throughout.

---

### 5. `app/routes/feed.py` — 2 async endpoints

**Endpoints converted:** `get_feed`, `get_shared_feed`

**Critical change — `currentUser.following` → direct connections table query:**
```python
# BEFORE (accesses relationship, triggers lazy load)
following_ids = [user.id for user in currentUser.following]

# AFTER (direct query on connections table)
from app.models import connections
following_result = await db.execute(
    select(connections.c.followed_id).where(connections.c.follower_id == currentUser.id)
)
following_ids = [row[0] for row in following_result.fetchall()]
```

**Feed query with `.in_()` filter:**
```python
posts_result = await db.execute(
    select(models.Post)
    .where(models.Post.owner_id.in_(following_ids))
    .order_by(models.Post.created_at.desc())
    .offset(skip).limit(limit)
)
posts = posts_result.scalars().all()
```

---

## Phases 3 & 4 — Summary

### What's Now Async

| Component | File Count | Endpoints |
|-----------|-----------|-----------|
| Auth routes | 1 file | 4 endpoints |
| Post routes | 1 file | 4 endpoints |
| User routes | 1 file | 7 endpoints |
| Like routes | 1 file | 2 endpoints |
| Connect routes | 1 file | 5 endpoints |
| Comment routes | 1 file | 4 endpoints |
| Search routes | 1 file | 1 endpoint |
| Me routes | 1 file | 11 endpoints |
| Change password routes | 1 file | 2 endpoints + 1 helper |
| Feed routes | 1 file | 2 endpoints |
| **Total** | **10 files** | **42 endpoints** |

### Recurring Patterns Applied

| Pattern | Old (sync) | New (async) |
|---------|-----------|-------------|
| Query single | `db.query(M).filter(...).first()` | `(await db.execute(select(M).where(...))).scalars().first()` |
| Query all | `db.query(M).filter(...).all()` | `(await db.execute(select(M).where(...))).scalars().all()` |
| Count | `db.query(M).filter(...).count()` | `(await db.execute(select(func.count()).select_from(M).where(...))).scalar()` |
| Insert | `db.add(obj)` + `db.commit()` + `db.refresh()` | `db.add(obj)` + `await db.commit()` + `await db.refresh(obj)` |
| Update | `db.query(M).filter(...).update(d)` | `await db.execute(update(M).where(...).values(**d))` |
| Delete | `db.delete(obj)` + `db.commit()` | `await db.delete(obj)` + `await db.commit()` |
| Bulk delete | `db.query(M).filter(...).delete()` | `await db.execute(delete(M).where(...))` |
| Rollback | `db.rollback()` | `await db.rollback()` |
| File write | `shutil.copyfileobj(f, buf)` | `aiofiles.open()` + `await buf.write(bytes)` |
| File delete | `os.remove(path)` | `await asyncio.to_thread(os.remove, path)` |
| Redis call | `redis_service.func()` | `await redis_service.func()` |
| M2M append | `user.following.append(target)` | `await db.execute(insert(table).values(...))` |
| M2M remove | `user.following.remove(target)` | `await db.execute(delete(table).where(...))` |

### What Remains

| Phase | Scope | Status |
|-------|-------|--------|
| Phase 5 | Chat system (~15 files) | ⏳ Deferred by user |
| Tests | conftest.py + all test files | ⏳ Deferred by user |

---