from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from app import models, schemas, oauth2 , db
import os

router = APIRouter(tags=["Feed"])

@router.get("/feed/home", response_model=schemas.FeedResponse)
def getHomeFeed(limit:int=Query(10, ge=1, le=100),
    offset: int = Query(0,ge=0),
    db:Session=Depends(db.getDb),
    currentUser:models.User=Depends(oauth2.getCurrentUser)
    ):
    # Get users the current user follows
    followed_users = [user.id for user in currentUser.following]
    
    # Query posts from followed users, recent first
    posts_query = db.query(models.Post).filter(models.Post.user_id.in_(followed_users)).order_by(models.Post.created_at.desc())
    total=posts_query.count()
    posts=posts_query.offset(offset).limit(limit).all()
    
    # Get liked post IDs
    liked_post_ids = {v.post_id for v in db.query(models.Votes).filter(models.Votes.user_id == currentUser.id, models.Votes.action == True).all()}
    
    # Build proper feed response
    user_homeFeed = []
    for post in posts:
        owner = schemas.UserOut(
            id=post.user_id,
            username=post.user.username,
            profile_pic=post.user.profile_picture
        )
        # Build the post item with is_liked
        post_item = schemas.PostListItemResponse(
            id=post.id,
            title=post.title,
            media_url=f"{os.getenv('BASE_URL', 'http://localhost:8000')}/{os.getenv('MEDIA_FOLDER', 'posts_media')}/{post.media_path}" if post.media_path else None,
            media_type=post.media_type,
            likes=post.likes,
            comments_count=post.comments_cnt,
            created_at=post.created_at,
            is_liked=post.id in liked_post_ids
        )
        
        user_homeFeed.append(schemas.FeedItemResponse(
            post_id=post.id,
            post=post_item,
            owner=owner
        ))
    
    return schemas.FeedResponse(feed=user_homeFeed, total=total)

@router.get("/feed/explore", response_model=schemas.PostListResponse)
def getExploreFeed(limit:int=Query(20, ge=1, le=100),
    offset: int = Query(0,ge=0),
    db:Session=Depends(db.getDb),
    currentUser:models.User=Depends(oauth2.getCurrentUser)
    ):
    # For explore, get all posts (or random) - excluding potentially private ones if that existed
    # Simple implementation: All recent posts
    posts_query = db.query(models.Post).order_by(models.Post.created_at.desc())
    total = posts_query.count()
    posts = posts_query.offset(offset).limit(limit).all()
    
    # Get liked post IDs
    liked_post_ids = {v.post_id for v in db.query(models.Votes).filter(models.Votes.user_id == currentUser.id, models.Votes.action == True).all()}
    
    # helper to format posts specifically for explore (similar to user posts list)
    explore_posts = []
    for post in posts:
        media_url = None
        if post.media_path:
            media_url = f"{os.getenv('BASE_URL', 'http://localhost:8000')}/{os.getenv('MEDIA_FOLDER', 'posts_media')}/{post.media_path}"
            
        explore_posts.append(schemas.PostListItemResponse(
            id=post.id,
            title=post.title,
            media_url=media_url,
            media_type=post.media_type,
            likes=post.likes,
            comments_count=post.comments_cnt,
            created_at=post.created_at,
            is_liked=post.id in liked_post_ids
        ))

    pagination = schemas.PaginationMetadata(
        total=total,
        limit=limit,
        offset=offset,
        has_more=(limit+offset)<total
    )
    
    return schemas.PostListResponse(posts=explore_posts, pagination=pagination)