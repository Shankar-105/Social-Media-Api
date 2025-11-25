def test_vote_on_post(client, get_token):
    # Create post first
    create = client.post("/posts/createPost", data={
        "title": "Like this Post",
        "content": "Like content"
    }, headers={"Authorization": f"Bearer {get_token}"})
    post_id = create.json().get("post", {}).get("id") or 1
    vote = {"post_id": post_id, "choice": True}
    resp = client.post("/vote/on_post", json=vote, headers={"Authorization": f"Bearer {get_token}"})
    assert resp.status_code == 201

def test_vote_on_nonexistent_post(client,get_token):
    vote = {"post_id": 69420, "choice": True}
    resp = client.post("/vote/on_post", json=vote, headers={"Authorization": f"Bearer {get_token}"})
    assert resp.status_code == 404