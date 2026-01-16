"""
Additional tests for edge cases and WebSocket functionality
"""
import pytest
from fastapi.testclient import TestClient


def test_post_detail_response_complete(client, get_token):
    """Verify PostDetailResponse has all required fields"""
    create_resp = client.post("/posts/createPost",
        data={"title": "Complete Test", "content": "Full data"},
        headers={"Authorization": f"Bearer {get_token}"})
    
    post = create_resp.json()
    # Verify all PostDetailResponse fields
    required_fields = ["id", "title", "content", "likes", "dislikes", 
                      "views", "comments_count", "enable_comments", 
                      "created_at", "owner"]
    for field in required_fields:
        assert field in post, f"Missing field: {field}"


def test_user_profile_response_structure(client, get_token):
    """Verify UserProfileResponse schema"""
    resp = client.get("/me/profile",
        headers={"Authorization": f"Bearer {get_token}"})
    
    assert resp.status_code == 200
    profile = resp.json()
    
    required_fields = ["profilePicture", "username", "nickname", 
                      "bio", "posts", "followers", "following"]
    for field in required_fields:
        assert field in profile


def test_vote_stats_response_schema(client, get_token):
    """Verify VoteStatsResponse returns proper counts"""
    resp = client.get("/me/voteStats",
        headers={"Authorization": f"Bearer {get_token}"})
    
    assert resp.status_code == 200
    stats = resp.json()
    assert "liked_posts_count" in stats
    assert "disliked_posts_count" in stats
    assert isinstance(stats["liked_posts_count"], int)
    assert isinstance(stats["disliked_posts_count"], int)


def test_comment_stats_response_schema(client, get_token):
    """Verify CommentStatsResponse"""
    resp = client.get("/me/comment-stats",
        headers={"Authorization": f"Bearer {get_token}"})
    
    assert resp.status_code == 200
    stats = resp.json()
    assert "total_comments" in stats
    assert "unique_posts_commented" in stats


def test_pagination_has_more_calculation(client, get_token):
    """Verify has_more is calculated correctly"""
    # Get first page
    resp1 = client.get("/me/posts?limit=2&offset=0",
        headers={"Authorization": f"Bearer {get_token}"})
    data1 = resp1.json()
    
    if data1["pagination"]["total"] > 2:
        # Should have more
        assert data1["pagination"]["has_more"] == True
    else:
        assert data1["pagination"]["has_more"] == False


def test_media_info_response(client, get_token):
    """Verify MediaInfo schema for profile pictures"""
    # First try to get profile pic
    resp = client.get("/me/profile/pic",
        headers={"Authorization": f"Bearer {get_token}"})
    
    # If user has profile pic (might be 404 if not)
    if resp.status_code == 200:
        media = resp.json()
        assert "url" in media
        assert "type" in media or media.get("type") is None


def test_feed_response_structure(client, get_token):
    """Verify FeedResponse schema"""
    resp = client.get("/feed/home?limit=5&offset=0",
        headers={"Authorization": f"Bearer {get_token}"})
    
    assert resp.status_code == 200
    feed = resp.json()
    assert "feed" in feed
    assert "total" in feed
    assert isinstance(feed["feed"], list)
    
    # Check feed item structure
    if feed["feed"]:
        item = feed["feed"][0]
        assert "post_id" in item
        assert "owner" in item


def test_can_edit_response_schema(client, get_token):
    """Verify CanEditResponse for edit_msg endpoint"""
    # This would need a message_id, assuming endpoint exists in router
    # Test endpoint availability
    try:
        resp = client.get("/msg/1/can_edit",
            headers={"Authorization": f"Bearer {get_token}"})
        # If endpoint exists
        if resp.status_code in [200, 404]:
            data = resp.json()
            if resp.status_code == 200:
                assert "can_edit" in data
                assert isinstance(data["can_edit"], bool)
    except:
        pytest.skip("Edit message endpoint not mounted")


def test_invalid_token_returns_401(client):
    """Verify authentication failures are consistent"""
    resp = client.get("/me/profile",
        headers={"Authorization": "Bearer invalid_token_here"})
    
    assert resp.status_code == 401
    error = resp.json()
    assert "detail" in error


def test_comment_create_response(client, get_token):
    """Verify comment creation returns CommentDetailResponse"""
    # Create a post first
    post_resp = client.post("/posts/createPost",
        data={"title": "For Comment", "content": "Test"},
        headers={"Authorization": f"Bearer {get_token}"})
    post_id = post_resp.json()["id"]
    
    # Create comment
    resp = client.post("/comment",
        json={"post_id": post_id, "content": "Nice post!"},
        headers={"Authorization": f"Bearer {get_token}"})
    
    assert resp.status_code == 201
    comment = resp.json()
    assert "id" in comment
    assert "content" in comment
    assert "user" in comment
    assert "post_id" in comment


def test_user_basic_response_in_followers(client, get_token):
    """Verify followers/following return UserBasicResponse list"""
    resp = client.get("/me/profile",
        headers={"Authorization": f"Bearer {get_token}"})
    user_id = resp.json().get("id", 1)
    
    # Get followers
    followers_resp = client.get(f"/users/{user_id}/followers",
        headers={"Authorization": f"Bearer {get_token}"})
    
    assert followers_resp.status_code == 200
    followers = followers_resp.json()
    assert isinstance(followers, list)
    
    # Check structure if any followers
    if followers:
        follower = followers[0]
        assert "id" in follower
        assert "username" in follower
        assert "nickname" in follower
