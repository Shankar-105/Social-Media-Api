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

# same username,password,hostname
TEST_DB_URL = (
    f"postgresql://{settings.database_user}:{settings.database_password}"
    f"@{settings.database_host}/{settings.database_name}_test"
)

test_engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# pytest fixtures very helpful
@pytest.fixture(scope="session",autouse=True)
def setup_test_db():
    # drop everything before creating optional checking for robustness
    Base.metadata.drop_all(bind=test_engine)
    # then create all tables
    Base.metadata.create_all(bind=test_engine)
    yield

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
