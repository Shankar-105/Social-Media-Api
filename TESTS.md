# Testing Guide

## 🧪 Running Tests with Pytest

This guide explains how to run tests for the FastAPI Social Media API after setup is complete.

---

## **Prerequisites**

Before running tests, ensure you have:

1. ✅ **Completed the setup** from [SETUP.md](./SETUP.md)
2. ✅ **Docker containers running** (`docker compose up -d`)
3. ✅ **Test database created** (happens automatically via `conftest.py`)

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

### **1. Run All Tests**

Execute all test files with verbose output:

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

Run tests from a single file:

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

Run a single test by name:

```bash
pytest pytests/test_auth.py::test_login_success -v
```

**Example:**
```bash
pytest pytests/test_posts.py::test_create_post -v
```

---

### **4. Run Tests with Different Output Options**

#### **Short Traceback** (cleaner output)
```bash
pytest pytests/ -v --tb=short
```

#### **No Traceback** (only show pass/fail)
```bash
pytest pytests/ -v --tb=no
```

#### **Show Print Statements** (see `print()` output)
```bash
pytest pytests/ -v -s
```

#### **Ignore Warnings**
```bash
pytest pytests/ -v -W ignore
```

#### **Combination** (verbose + show prints + ignore warnings)
```bash
pytest pytests/ -v -s -W ignore
```

---

### **5. Run Tests with Coverage Report**

See how much of your code is tested:

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

```bash
pytest pytests/ --lf -v
```

**`--lf`** = "last failed"

---

### **7. Run Tests Matching a Pattern**

Run all tests with "post" in the name:

```bash
pytest pytests/ -k "post" -v
```

Run all tests with "user" in the name:

```bash
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

**Solution:** Install pytest
```bash
pip install pytest
```

### **Issue: "Connection refused" errors**

**Solution:** Ensure Docker containers are running
```bash
docker compose ps  # Check if running
docker compose up -d  # Start if not running
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

# Run tests again
pytest pytests/ -v
```

### **Issue: Import errors in tests**

**Solution:** Run pytest from the project root directory:
```bash
cd /path/to/fastApiProject
pytest pytests/ -v
```

---

## **🎯 Best Practices**

1. ✅ **Always run from project root**
   ```bash
   cd fastApiProject/
   pytest pytests/ -v
   ```

2. ✅ **Use `-v` for readable output**
   - See which tests pass/fail clearly

3. ✅ **Run tests before committing changes**
   ```bash
   pytest pytests/ --tb=short
   ```

4. ✅ **Write tests for new features**
   - Add to appropriate test file in `pytests/`

5. ✅ **Keep tests isolated**
   - Each test should be independent
   - Use fixtures for setup

6. ✅ **Test both success and failure cases**
   - Test happy path + error cases

---

## **📚 Quick Reference**

### **Most Common Commands**

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
2. 🧪 **Write more tests** for new features
3. 🔍 **Check test coverage** with `pytest --cov`
4. 📝 **Review** `conftest.py` to understand fixtures

---

## **📞 Need Help?**

- 📋 Check existing tests in `pytests/` for examples
- 📚 Read [official pytest docs](https://docs.pytest.org/)
- 🐛 Review test output carefully for error details

---

**Happy Testing! 🧪🚀**
