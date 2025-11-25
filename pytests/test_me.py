def test_my_profile(client, get_token):
    resp = client.get("/me/profile", headers={"Authorization": f"Bearer {get_token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"

def test_update_user_info(client, get_token):
    resp = client.patch("/me/updateInfo", data={"bio": "updated bio"}, headers={"Authorization": f"Bearer {get_token}"})
    assert resp.status_code == 200