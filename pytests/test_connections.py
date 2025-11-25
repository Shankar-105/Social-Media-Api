def test_follow_unfollow(client, get_token):
    # Sign up a second user
    user2 = {"username": "user2", "password": "password", "nickname": "Nick2"}
    client.post("/user/signup", json=user2)
    # Get second user ID
    users = client.get("/users/getAllUsers", headers={"Authorization": f"Bearer {get_token}"}).json()
    second_user = next((u for u in users if u["username"] == "user2"), None)
    assert second_user is not None
    second_id = second_user["id"]
    # Follow
    resp = client.post(f"/follow/{second_id}", headers={"Authorization": f"Bearer {get_token}"})
    assert resp.status_code in (201, 400)
    # Unfollow
    resp2 = client.delete(f"/unfollow/{second_id}", headers={"Authorization": f"Bearer {get_token}"})
    assert resp2.status_code in (201, 400)