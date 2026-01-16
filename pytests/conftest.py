import pytest
import os,sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient # fastapi.testclient needs starlette.testclient which again needs httpx module

# pytest doesnt see anything except the tests sub-folder so we need to add the
# project path to pythonpath so that now pytest can see all the project fplders

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# after setting the PYTHONPATH then import anyother foldes in project dir
from app.main import app
from app.models import Base
from app.db import getDb
from app.config import settings

# SMART DATABASE HOST DETECTION FOR DOCKER vs LOCAL

def get_test_database_host():
    """
    Automatically detect if running in Docker container and return appropriate host.
    
    Detection methods (in order):
    1. Check for /.dockerenv file (exists in Docker containers)
    2. Check if DATABASE_HOST env var is explicitly set to 'db'
    3. Fall back to settings.database_host (localhost for local testing)
    
    Returns:
        str: 'db' if in Docker, 'localhost' (or custom) if local
    """
    # Method 1: Check for Docker environment file
    if os.path.exists('/.dockerenv'):
        return 'db'
    
    # Method 2: Check environment variable override
    env_host = os.getenv('DATABASE_HOST')
    if env_host and env_host == 'db':
        return 'db'
    
    # Method 3: Default to settings (localhost for local testing)
    return settings.database_host

# Use smart detection
TEST_DATABASE_HOST = get_test_database_host()

# PostgreSQL is case-insensitive by default and converts unquoted names to lowercase.
# We standardize on lowercase to prevent mismatches between creation and connection.
TEST_DB_NAME = f"{settings.database_name}_test".lower()

# Construct test database URL with detected host and standardized lowercase name
TEST_DB_URL = (
    f"postgresql://{settings.database_user}:{settings.database_password}"
    f"@{TEST_DATABASE_HOST}/{TEST_DB_NAME}"
)

# Debug output to verify detection (helpful for troubleshooting)
print(f"🔍 Test DB Host detected: {TEST_DATABASE_HOST}")
print(f"🔗 Test DB URL: postgresql://***:***@{TEST_DATABASE_HOST}/{TEST_DB_NAME}")

# CREATE TEST DATABASE IF IT DOESN'T EXIST

def create_test_database_if_not_exists():
    """
    Create the test database if it doesn't exist.
    Connects to the default 'postgres' database to create our test database.
    """
    from sqlalchemy import text
    from sqlalchemy.exc import ProgrammingError
    
    # Connect to default 'postgres' database to allow DB creation
    default_db_url = (
        f"postgresql://{settings.database_user}:{settings.database_password}"
        f"@{TEST_DATABASE_HOST}/postgres"
    )
    
    default_engine = create_engine(default_db_url, isolation_level="AUTOCOMMIT")
    
    try:
        with default_engine.connect() as conn:
            # Check if database exists (using the same lowercase name)
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": TEST_DB_NAME}
            )
            exists = result.scalar() is not None
            
            if not exists:
                print(f"📦 Creating test database: {TEST_DB_NAME}")
                # We use a f-string for the database name in CREATE DATABASE as it can't be parameterized
                conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
                print(f"✅ Test database created successfully!")
            else:
                print(f"✅ Test database already exists: {TEST_DB_NAME}")
    except ProgrammingError as e:
        if "already exists" in str(e).lower():
            print(f"✅ Test database already exists: {TEST_DB_NAME}")
        else:
            print(f"⚠️  Programming Error: {e}")
            raise
    except Exception as e:
        print(f"⚠️  Error checking/creating test database: {e}")
        raise
    finally:
        default_engine.dispose()

# Create test database before creating engine
create_test_database_if_not_exists()

test_engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# pytest fixtures very helpful
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Setup: Drop and recreate tables for a clean start
    print("🗑️  Dropping all existing tables...")
    Base.metadata.drop_all(bind=test_engine)
    print("🏗️  Creating all tables...")
    Base.metadata.create_all(bind=test_engine)
    print("✅ Test database setup complete!")
    yield
    # Teardown: Delete the test database after all tests are finished
    print(f"\n🧹 Cleaning up test database: {TEST_DB_NAME}...")
    # First, dispose the test engine to close all active connections
    test_engine.dispose()
    from sqlalchemy import text
    # Connect to the default 'postgres' database to perform the drop
    cleanup_db_url = (
        f"postgresql://{settings.database_user}:{settings.database_password}"
        f"@{TEST_DATABASE_HOST}/postgres"
    )
    cleanup_engine = create_engine(cleanup_db_url, isolation_level="AUTOCOMMIT")
    try:
        with cleanup_engine.connect() as conn:
            # PostgreSQL 13+ supports WITH (FORCE) to drop DB with active connections
            # We try WITH (FORCE) first, then fall back to standard DROP if it fails
            try:
                conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)'))
            except Exception:
                # Fallback for older PostgreSQL versions that don't support WITH (FORCE)
                conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"'))
            print(f"✅ Test database '{TEST_DB_NAME}' deleted successfully!")
    except Exception as e:
        print(f"⚠️  Error deleting test database: {e}")
    finally:
        cleanup_engine.dispose()

def override_getDb():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# ovveride the actual dependency
app.dependency_overrides[getDb] = override_getDb

# using the TestClient to call routes wihtout any extra tool
@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session")
def create_test_user(client):
    user_data = {
        "username": "testuser",
        "password": "testpassword",
        "nickname": "TestUser"
    }
    resp = client.post("/user/signup", json=user_data)
    assert resp.status_code in (201, 409)  # 201=created, 409=already exists
    return user_data

# preserve the token!
@pytest.fixture(scope="session")
def get_token(client,create_test_user):
    data = {
        "username": create_test_user["username"],
        "password": create_test_user["password"]
    }
    resp = client.post("/login", data=data)
    assert resp.status_code == 202
    token = resp.json()["accessToken"]
    return token
