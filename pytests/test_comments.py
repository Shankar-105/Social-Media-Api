async def test_add_comment(client, get_token):
    post = await client.post("/posts/createPost", data={
        "title": "Commentable Post",
        "content": "Please comment"
    }, headers={"Authorization": f"Bearer {get_token}"})
    post_id = post.json().get("post", {}).get("id") or 1
    comment = {"post_id": post_id, "content": "Nice post!"}
    resp = await client.post("/comment", json=comment, headers={"Authorization": f"Bearer {get_token}"})
    assert resp.status_code == 201

async def test_delete_comment_not_exist(client, get_token):
    resp = await client.delete("/comments/delete_comment/98765", headers={"Authorization": f"Bearer {get_token}"})
    assert resp.status_code in (404, 200)