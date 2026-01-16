# Testing Guide

## 🧪 Running Tests with Pytest

This guide explains how to run tests for the FastAPI Social Media API after setup is complete.

---

## **Prerequisites**

Before running tests, ensure you have:

1. ✅ **Completed the setup** from [SETUP.md](./SETUP.md)
2. ✅ **Docker containers running** (`docker compose up -d`)
   - **Important:** After running `docker compose up -d`, containers run in detached mode
   - The database is accessible, but you need to choose how to run pytest (see below)
3. ✅ **Test database created** (happens automatically via `conftest.py`)

---

## **🔧 How to Run Tests: Two Options**

Since your code and dependencies are inside Docker containers, you have **two ways** to run tests:

### **Option 1: Run Tests Inside Docker Container** (Recommended)

**Best for:** Most users, ensures consistent environment

**Requirements:**
- ✅ Docker containers running (`docker compose up -d`)
- ✅ No local Python/pytest installation needed

**How to run:**
```bash
# Run all tests inside the API container
docker compose exec api pytest pytests/ -v

# Run specific test file
docker compose exec api pytest pytests/test_auth.py -v

# Run specific test function
docker compose exec api pytest pytests/test_auth.py::test_login_success -v
```

**Why this works:**
- Pytest and all dependencies are already installed in the container
- Database connection uses `DATABASE_HOST=db` (container networking)
- No need to install anything locally

---

### **Option 2: Run Tests Locally** (Alternative)

**Best for:** Developers who prefer local development tools

**Requirements:**
- ✅ Docker containers running (`docker compose up -d`)
- ✅ Python 3.12+ installed locally
- ✅ Pytest and dependencies installed locally
- ✅ **`.env` file must have `DATABASE_HOST=localhost`** (not `db`)

**Setup steps:**

1. **Install dependencies locally:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Update `.env` file:**
   - Change `DATABASE_HOST=db` to `DATABASE_HOST=localhost`
   - This allows local pytest to connect to the database exposed on port 5432

3. **Run tests:**
   ```bash
   # From project root directory
   pytest pytests/ -v
   ```

**Note:** If you switch between local and container testing, remember to update `DATABASE_HOST` in `.env` accordingly:
- `DATABASE_HOST=db` → for running inside container
- `DATABASE_HOST=localhost` → for running locally

---

## **📁 Test Structure**

All tests are located in the `pytests/` directory:

```
pytests/
├── conftest.py              # Test configuration & fixtures
├── test_auth.py             # Authentication tests
├── test_posts.py            # Post CRUD tests
├── test_comments.py         # Comment tests
├── test_votes.py            # Like/dislike tests
├── test_users.py            # User profile tests
├── test_me.py               # Current user tests
├── test_connections.py      # Follow/unfollow tests
├── test_chat.py             # WebSocket chat tests
├── test_schema_validation.py # Schema validation tests
└── test_edge_cases.py       # Edge case & integration tests
```

---

## **⚙️ Test Database**

Tests use a **separate test database** to avoid polluting your development data:

- **Main DB**: `fastapi_sm` (from `.env`)
- **Test DB**: `fastapi_sm_test` (automatically created)

The test database is:
- ✅ Created automatically on first test run
- ✅ Cleared and rebuilt before each test session
- ✅ Isolated from your development database

---

## **🚀 Running Tests**

> **💡 Quick Start:** If you're using **Option 1 (Docker)**, prefix all commands with `docker compose exec api`
> 
> Example: `docker compose exec api pytest pytests/ -v`

### **1. Run All Tests**

**Inside Docker Container:**
```bash
docker compose exec api pytest pytests/ -v
```

**Locally (if configured):**
```bash
pytest pytests/ -v
```

**Expected Output:**
```
pytests/test_auth.py::test_login_success PASSED                    [ 10%]
pytests/test_auth.py::test_login_wrong_password PASSED             [ 20%]
pytests/test_posts.py::test_create_post PASSED                     [ 30%]
pytests/test_posts.py::test_get_post PASSED                        [ 40%]
...
======================== 25 passed in 5.23s =========================
```

---

### **2. Run Specific Test File**

**Inside Docker Container:**
```bash
# Test only authentication
docker compose exec api pytest pytests/test_auth.py -v

# Test only posts
docker compose exec api pytest pytests/test_posts.py -v

# Test schema validation
docker compose exec api pytest pytests/test_schema_validation.py -v
```

**Locally (if configured):**
```bash
# Test only authentication
pytest pytests/test_auth.py -v

# Test only posts
pytest pytests/test_posts.py -v

# Test schema validation
pytest pytests/test_schema_validation.py -v
```

---

### **3. Run Specific Test Function**

**Inside Docker Container:**
```bash
docker compose exec api pytest pytests/test_auth.py::test_login_success -v
```

**Locally (if configured):**
```bash
pytest pytests/test_auth.py::test_login_success -v
```

**Example:**
```bash
# Inside container
docker compose exec api pytest pytests/test_posts.py::test_create_post -v

# Or locally
pytest pytests/test_posts.py::test_create_post -v
```

---

### **4. Run Tests with Different Output Options**

**Inside Docker Container:**
```bash
# Short traceback (cleaner output)
docker compose exec api pytest pytests/ -v --tb=short

# No traceback (only show pass/fail)
docker compose exec api pytest pytests/ -v --tb=no

# Show print statements (see print() output)
docker compose exec api pytest pytests/ -v -s

# Ignore warnings
docker compose exec api pytest pytests/ -v -W ignore

# Combination (verbose + show prints + ignore warnings)
docker compose exec api pytest pytests/ -v -s -W ignore
```

**Locally (if configured):**
```bash
# Short traceback (cleaner output)
pytest pytests/ -v --tb=short

# No traceback (only show pass/fail)
pytest pytests/ -v --tb=no

# Show print statements (see print() output)
pytest pytests/ -v -s

# Ignore warnings
pytest pytests/ -v -W ignore

# Combination (verbose + show prints + ignore warnings)
pytest pytests/ -v -s -W ignore
```

---

### **5. Run Tests with Coverage Report**

See how much of your code is tested:

**Inside Docker Container:**
```bash
# Run with coverage (pytest-cov already installed in container)
docker compose exec api pytest pytests/ --cov=app --cov-report=html

# View coverage report (files created in container, accessible via volume mount)
# Open htmlcov/index.html in your browser
```

**Locally (if configured):**
```bash
# Install coverage first (if not installed)
pip install pytest-cov

# Run with coverage
pytest pytests/ --cov=app --cov-report=html

# View coverage report
# Open htmlcov/index.html in your browser
```

---

### **6. Run Failed Tests Only** (after a test run)

Re-run only the tests that failed:

**Inside Docker Container:**
```bash
docker compose exec api pytest pytests/ --lf -v
```

**Locally (if configured):**
```bash
pytest pytests/ --lf -v
```

**`--lf`** = "last failed"

---

### **7. Run Tests Matching a Pattern**

**Inside Docker Container:**
```bash
# Run all tests with "post" in the name
docker compose exec api pytest pytests/ -k "post" -v

# Run all tests with "user" in the name
docker compose exec api pytest pytests/ -k "user" -v
```

**Locally (if configured):**
```bash
# Run all tests with "post" in the name
pytest pytests/ -k "post" -v

# Run all tests with "user" in the name
pytest pytests/ -k "user" -v
```

---

## **📊 Common pytest Options**

| Option | Description | Example |
|--------|-------------|---------|
| `-v` | Verbose output | `pytest -v` |
| `-s` | Show print statements | `pytest -s` |
| `-x` | Stop on first failure | `pytest -x` |
| `--lf` | Run last failed tests | `pytest --lf` |
| `--tb=short` | Shorter traceback | `pytest --tb=short` |
| `--tb=no` | No traceback | `pytest --tb=no` |
| `-W ignore` | Ignore warnings | `pytest -W ignore` |
| `-k "pattern"` | Run tests matching pattern | `pytest -k "auth"` |
| `--maxfail=2` | Stop after 2 failures | `pytest --maxfail=2` |
| `--durations=10` | Show 10 slowest tests | `pytest --durations=10` |

---

## **🔍 Understanding Test Output**

### **Successful Test**
```
pytests/test_auth.py::test_login_success PASSED                    [100%]
```
- ✅ **PASSED** = Test succeeded

### **Failed Test**
```
pytests/test_posts.py::test_create_post FAILED                     [50%]

=========================== FAILURES ===========================
___________________ test_create_post ___________________

    def test_create_post(client, get_token):
        data = {"title": "Test", "content": "Content"}
        resp = client.post("/posts/createPost", ...)
>       assert resp.status_code == 201
E       assert 422 == 201

pytests/test_posts.py:7: AssertionError
```
- ❌ **FAILED** = Test failed
- Shows which assertion failed and why

### **Skipped Test**
```
pytests/test_chat.py::test_websocket SKIPPED                       [75%]
```
- ⏭️ **SKIPPED** = Test was skipped (usually conditional)

---

## **🐛 Debugging Failed Tests**

### **1. Run with More Detail**
```bash
pytest pytests/test_posts.py::test_create_post -vv
```
- `-vv` = Extra verbose

### **2. Drop into Debugger on Failure**
```bash
pytest pytests/ --pdb
```
- Automatically opens Python debugger when a test fails

### **3. Show Local Variables**
```bash
pytest pytests/ -l
```
- Shows local variables in traceback

---

## **📝 Writing New Tests**

### **Basic Test Structure**

```python
def test_your_feature(client, get_token):
    """Test description"""
    # Arrange - setup data
    data = {"key": "value"}
    
    # Act - perform action
    resp = client.post("/endpoint", json=data, 
        headers={"Authorization": f"Bearer {get_token}"})
    
    # Assert - verify result
    assert resp.status_code == 201
    assert "expected_field" in resp.json()
```

### **Using Fixtures**

Available fixtures (from `conftest.py`):

- **`client`** - TestClient for making API requests
- **`get_token`** - Valid auth token
- **`create_test_user`** - Test user data

```python
def test_with_fixtures(client, get_token, create_test_user):
    # client, get_token, and create_test_user are automatically provided
    resp = client.get("/me/profile", 
        headers={"Authorization": f"Bearer {get_token}"})
    assert resp.status_code == 200
```

---

## **⚠️ Troubleshooting**

### **Issue: "No module named 'pytest'"**

**If running locally:**
```bash
# Install pytest and dependencies
pip install -r requirements.txt
```

**If running in Docker:**
- Pytest is already installed in the container
- Use: `docker compose exec api pytest pytests/ -v`

### **Issue: "Connection refused" or database connection errors**

**Solution 1:** Ensure Docker containers are running
```bash
docker compose ps  # Check if running
docker compose up -d  # Start if not running
```

**Solution 2:** Check your `.env` file `DATABASE_HOST` setting
- **If running tests inside Docker container:** `DATABASE_HOST=db`
- **If running tests locally:** `DATABASE_HOST=localhost` (or `127.0.0.1`)

**Solution 3:** Verify database is accessible
```bash
# Check if database port is exposed
docker compose ps  # Should show db container with port 5432:5432

# Test connection from host (if running locally)
# Should work if DATABASE_HOST=localhost in .env
```

### **Issue: Tests fail with database errors**

**Solution:** The test database may be in a bad state. Drop and recreate:
```bash
# Stop containers
docker compose down

# Remove volumes (deletes test DB)
docker compose down --volumes

# Restart
docker compose up -d

# Run tests again (inside container)
docker compose exec api pytest pytests/ -v

# Or locally (if configured)
pytest pytests/ -v
```

### **Issue: Import errors in tests**

**If running locally:**
```bash
# Run pytest from the project root directory
cd /path/to/fastApiProject
pytest pytests/ -v
```

**If running in Docker:**
- Import errors shouldn't occur (container has correct paths)
- Use: `docker compose exec api pytest pytests/ -v`

---

## **🎯 Best Practices**

1. ✅ **Choose your testing method**
   - **Recommended:** Run tests inside Docker container (no local setup needed)
   - **Alternative:** Run locally (requires local Python + dependencies)

2. ✅ **Always run from project root**
   ```bash
   # Inside container
   docker compose exec api pytest pytests/ -v
   
   # Or locally
   cd fastApiProject/
   pytest pytests/ -v
   ```

3. ✅ **Use `-v` for readable output**
   - See which tests pass/fail clearly

4. ✅ **Run tests before committing changes**
   ```bash
   # Inside container
   docker compose exec api pytest pytests/ --tb=short
   
   # Or locally
   pytest pytests/ --tb=short
   ```

5. ✅ **Write tests for new features**
   - Add to appropriate test file in `pytests/`

6. ✅ **Keep tests isolated**
   - Each test should be independent
   - Use fixtures for setup

7. ✅ **Test both success and failure cases**
   - Test happy path + error cases

8. ✅ **Check `.env` DATABASE_HOST setting**
   - `DATABASE_HOST=db` for container testing
   - `DATABASE_HOST=localhost` for local testing

---

## **📚 Quick Reference**

### **Most Common Commands (Inside Docker Container - Recommended)**

```bash
# Run all tests
docker compose exec api pytest pytests/ -v

# Run all tests (no warnings)
docker compose exec api pytest pytests/ -v -W ignore

# Run all tests (short traceback)
docker compose exec api pytest pytests/ -v --tb=short

# Run specific file
docker compose exec api pytest pytests/test_auth.py -v

# Run specific test
docker compose exec api pytest pytests/test_auth.py::test_login_success -v

# Run with prints visible
docker compose exec api pytest pytests/ -v -s

# Run failed tests only
docker compose exec api pytest pytests/ --lf -v

# Stop on first failure
docker compose exec api pytest pytests/ -x -v
```

### **Most Common Commands (Local - If Configured)**

```bash
# Run all tests
pytest pytests/ -v

# Run all tests (no warnings)
pytest pytests/ -v -W ignore

# Run all tests (short traceback)
pytest pytests/ -v --tb=short

# Run specific file
pytest pytests/test_auth.py -v

# Run specific test
pytest pytests/test_auth.py::test_login_success -v

# Run with prints visible
pytest pytests/ -v -s

# Run failed tests only
pytest pytests/ --lf -v

# Stop on first failure
pytest pytests/ -x -v
```

---

## **🎓 Next Steps**

After running tests successfully:

1. 📖 **Explore the API docs**: http://localhost:8000/docs
2. 🧪 **Write more tests** for new features and raise an issue and send a PR I Love Contributions.
3. 🔍 **Check test coverage** with `pytest --cov`
4. 📝 **Review** `conftest.py` to understand fixtures

---

## **Need Help?**

- 📋 Check existing tests in `pytests/` for examples
- 📚 Read [official pytest docs](https://docs.pytest.org/)
- 🐛 Review test output carefully for error details

---

**Thank you! 🧪🚀**
