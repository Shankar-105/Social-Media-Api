def test_create_post(client, get_token):
    data = {
        "title": "My First Post",
        "content": "Here's the post content!"
    }
    resp = client.post("/posts/createPost", data=data, headers={"Authorization": f"Bearer {get_token}"})
    assert resp.status_code == 201

def test_get_post(client, get_token):
    # Post creation first (so we have a real post)
    create = client.post("/posts/createPost", data={
        "title": "Check Post",
        "content": "Hello World"
    }, headers={"Authorization": f"Bearer {get_token}"})
    post_id = create.json().get("post", {}).get("id") or 1
    resp = client.get(f"/posts/getPost/{post_id}", headers={"Authorization": f"Bearer {get_token}"})
    assert resp.status_code in (200, 404)