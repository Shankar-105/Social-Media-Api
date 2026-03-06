async def test_login_success(client, create_test_user):
    data = {
        "username": "testuser",
        "password": "testpassword",
    }
    resp = await client.post("/login", data=data)
    assert resp.status_code == 202
    assert "accessToken" in resp.json()

async def test_login_wrong_password(client, create_test_user):
    data = {
        "username": "testuser",
        "password": "wrongpassword",
    }
    resp = await client.post("/login", data=data)
    assert resp.status_code == 401