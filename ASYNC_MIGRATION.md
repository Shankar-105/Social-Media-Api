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
