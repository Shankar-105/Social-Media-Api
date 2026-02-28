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
