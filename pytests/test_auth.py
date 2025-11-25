def test_login_success(client,create_test_user):
    data = {
        "username": "testuser",
        "password": "testpassword",
    }
    resp = client.post("/login",data=data)
    assert resp.status_code == 202
    assert "accessToken" in resp.json()

def test_login_wrong_password(client,create_test_user):
    data = {
        "username": "testuser",
        "password": "wrongpassword",
    }
    resp = client.post("/login", data=data)
    assert resp.status_code == 404