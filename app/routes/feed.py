from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from app import models, schemas, oauth2 , db
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
    
    # Build proper feed response
    user_homeFeed = []
    for post in posts:
        owner = schemas.UserOut(
            id=post.user_id,
            username=post.user.username,
            profile_pic=post.user.profile_picture
        )
        user_homeFeed.append(schemas.FeedPost(
            post_id=post.id,
            owner=owner
        ))
    
    return schemas.FeedResponse(feed=user_homeFeed, total=total)