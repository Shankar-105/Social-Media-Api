def test_signup_new_user(client):
    new_user = {
        "username": "alice",
        "password": "supersecurepw",
        "nickname": "Alice"
    }
    resp = client.post("/user/signup", json=new_user)
    assert resp.status_code in (201, 409)

def test_get_all_users(client, get_token):
    resp = client.get("/users/getAllUsers", headers={"Authorization": f"Bearer {get_token}"})
    assert resp.status_code == 201
    assert isinstance(resp.json(), list)