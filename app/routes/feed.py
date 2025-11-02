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
    followed_users = [users.id for users in currentUser.following]
    """"if not followed_users:
        # Fallback to explore if no follows
        return get_explore_feed(skip=skip, limit=limit, db=db, current_user=current_user)"""
    
    # Query posts from followed users, recent first
    posts_query = db.query(models.Post).filter(models.Post.user_id.in_(followed_users)).order_by(models.Post.created_at.desc())
    total=posts_query.count()
    posts=posts_query.offset(offset).limit(limit).all()
    user_homeFeed = []
    for post in posts:
        owner=schemas.UserOut(id=post.user_id,username=post.user.username,profile_pic=post.user.profile_picture)
        user_homeFeed.append(schemas.FeedPost(
            post_id=post.id,
            owner=owner
            ))
    return {"feed": user_homeFeed,"total":total}