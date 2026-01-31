from fastapi import status,HTTPException,Depends,Body,APIRouter
import app.schemas as sch
from app import models,oauth2
from app.db import getDb
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from typing import List

router=APIRouter(tags=['connections'])

@router.post("/follow/{user_id}",status_code=status.HTTP_201_CREATED, response_model=sch.FollowResponse)
def follow(user_id:int,db:Session=Depends(getDb),currentUser:models.User=Depends(oauth2.getCurrentUser)):
    userToFollow=db.query(models.User).filter(models.User.id==user_id).first()
    if not userToFollow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User doesnt exist")
    if userToFollow.id == currentUser.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Cannot follow yourself")
    if userToFollow in currentUser.following:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Your already following this user")
    try:
        currentUser.following.append(userToFollow)
        currentUser.following_cnt=len(currentUser.following)
        userToFollow.followers_cnt=len(userToFollow.followers)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to follow user")
    return sch.FollowResponse(message=f"Followed user {userToFollow.username}", following_count=currentUser.following_cnt)
    
@router.delete("/unfollow/{user_id}",status_code=status.HTTP_200_OK, response_model=sch.FollowResponse)
def unfollow(user_id:int,db:Session=Depends(getDb),currentUser:models.User=Depends(oauth2.getCurrentUser)):
    userToUnFollow=db.query(models.User).filter(models.User.id==user_id).first()
    if not userToUnFollow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User doesnt exist")
    if userToUnFollow not in currentUser.following:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Not following this user")
    try:
        currentUser.following.remove(userToUnFollow)
        currentUser.following_cnt=len(currentUser.following)
        userToUnFollow.followers_cnt=len(userToUnFollow.followers)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to unfollow user")
    return sch.FollowResponse(message=f"Unfollowed user {userToUnFollow.username}", following_count=currentUser.following_cnt)

@router.delete("/remove_follower/{user_id}", status_code=status.HTTP_200_OK, response_model=sch.FollowResponse)
def remove_follower(user_id: int, db: Session = Depends(getDb), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    userToRemove = db.query(models.User).filter(models.User.id == user_id).first()
    if not userToRemove:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist")
    
    # Check if this user is actually following me
    if userToRemove not in currentUser.followers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user is not following you")

    try:
        # Remove them from my followers list
        currentUser.followers.remove(userToRemove)
        
        # Update counts
        currentUser.followers_cnt = len(currentUser.followers)
        userToRemove.following_cnt = len(userToRemove.following) # They are following me, so their following count decreases
        
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to remove follower")
        
    return sch.FollowResponse(message=f"Removed follower {userToRemove.username}", following_count=currentUser.following_cnt)

@router.get("/users/{user_id}/followers", response_model=List[sch.UserBasicResponse])
def get_followers(user_id:int,db:Session=Depends(getDb), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    user=db.query(models.User).filter(models.User.id==user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return [
        sch.UserBasicResponse(
            id=f.id,
            username=f.username,
            nickname=f.nickname,
            profile_pic=f.profile_picture,
            is_following=(f in currentUser.following)
        ) for f in user.followers
    ]

@router.get("/users/{user_id}/following", response_model=List[sch.UserBasicResponse])
def get_following(user_id:int,db:Session=Depends(getDb), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    user=db.query(models.User).filter(models.User.id==user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return [
        sch.UserBasicResponse(
            id=f.id,
            username=f.username,
            nickname=f.nickname,
            profile_pic=f.profile_picture,
            is_following=(f in currentUser.following)
        ) for f in user.following
    ]