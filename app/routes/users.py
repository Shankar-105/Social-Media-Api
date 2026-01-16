from fastapi import status,HTTPException,Depends,Body,APIRouter,Query
from typing import List
import app.schemas as sch
from app import models,db,oauth2
from sqlalchemy.orm import Session
import app.my_utils.utils as utils
import os
router=APIRouter(
    tags=['Users']
)
@router.get("/users/{user_id}/profile",status_code=status.HTTP_200_OK,response_model=sch.UserProfile)
def userProfile(user_id:int,db:Session=Depends(db.getDb),currentUser:models.User=Depends(oauth2.getCurrentUser)):
    user=db.query(models.User).filter(models.User.id==user_id).first()
    userProfile=sch.UserProfile(
        profilePicture=user.profile_picture,
        username=user.username,
        nickname=user.nickname,
        bio=user.bio,
        posts=len(user.posts),
        followers=user.followers_cnt,
        following=user.following_cnt,
    )
    if not userProfile.bio:
        userProfile.bio=""
    if not userProfile.profilePicture:
        userProfile.profilePicture="no profile picture"
    return userProfile

@router.get("/users/{user_id}/profile/pic",status_code=status.HTTP_200_OK, response_model=sch.MediaInfo)
def myProfilePicture(user_id:int,db:Session=Depends(db.getDb),currentUser:models.User=Depends(oauth2.getCurrentUser)):
    # get the current users profile pic
    user=db.query(models.User).filter(models.User.id==user_id).first()
    profilePicturePath = user.profile_picture
    # if he doesnt have a porfile pic return 404
    if not profilePicturePath:
        raise HTTPException(status_code=404, detail="No profile picture")
    file_path=f"profilepics/{profilePicturePath}"
    # optional check
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    # return proper schema with full URL
    return sch.MediaInfo(
        url=f"{os.getenv('BASE_URL', 'http://localhost:8000')}/profilepics/{profilePicturePath}",
        type="image"
    )

@router.post("/user/signup",status_code=status.HTTP_201_CREATED,response_model=sch.UserResponse)
def createUser(userData:sch.UserEssentials=Body(...),db:Session=Depends(db.getDb)):
    # hash the password using the bcrypt lib
    hashedPw=utils.hashPassword(userData.password)
    userData.password=hashedPw
    newUser=models.User(**userData.dict())
    db.add(newUser)
    db.commit()
    db.refresh(newUser)
    return newUser

@router.get("/users/getAllUsers",status_code=status.HTTP_201_CREATED,response_model=List[sch.UserResponse])
def getAllUsers(db:Session=Depends(db.getDb)):
    allUsers=db.query(models.User).all()
    return allUsers

@router.get("/users/{user_id}/followers",status_code=status.HTTP_200_OK, response_model=List[sch.UserBasicResponse])
def get_followers(user_id:int,db:Session=Depends(db.getDb),currentUser:models.User=Depends(oauth2.getCurrentUser)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    # Build proper response
    followers = []
    for follower in user.followers:
        followers.append(sch.UserBasicResponse(
            id=follower.id,
            username=follower.username,
            nickname=follower.nickname,
            profile_pic=follower.profile_picture
        ))
    return followers

@router.get("/users/{user_id}/following",status_code=status.HTTP_200_OK, response_model=List[sch.UserBasicResponse])
def get_following(user_id:int,db:Session=Depends(db.getDb),currentUser:models.User=Depends(oauth2.getCurrentUser)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    # Build proper response
    following = []
    for followed_user in user.following:
        following.append(sch.UserBasicResponse(
            id=followed_user.id,
            username=followed_user.username,
            nickname=followed_user.nickname,
            profile_pic=followed_user.profile_picture
        ))
    return following

@router.get("/users/{user_id}/posts", response_model=sch.PostListResponse)  
def getAllPosts(user_id:int,limit:int=Query(10, ge=1, le=100),
    offset: int = Query(0,ge=0),
    db:Session=Depends(db.getDb),
    currentUser:models.User=Depends(oauth2.getCurrentUser)
    ):
    # calculate the total number of posts of the user
    total=db.query(models.Post).filter(models.Post.user_id==user_id).count()
    # only fetch the first 'limit' posts after skipping the first 'offset' posts
    # and order them by the latest as first
    paginatedPosts=db.query(models.Post).filter(models.Post.user_id==user_id).order_by(models.Post.created_at.desc()).offset(offset).limit(limit).all()
    
    # Build proper response
    posts = []
    for post in paginatedPosts:
        media_url = None
        if post.media_path:
            media_url = f"{os.getenv('BASE_URL', 'http://localhost:8000')}/{os.getenv('MEDIA_FOLDER', 'posts_media')}/{post.media_path}"
        posts.append(sch.PostListItemResponse(
            id=post.id,
            title=post.title,
            media_url=media_url,
            media_type=post.media_type,
            likes=post.likes,
            comments_count=post.comments_cnt,
            created_at=post.created_at
        ))
    
    pagination = sch.PaginationMetadata(
        total=total,
        limit=limit,
        offset=offset,
        has_more=(limit+offset)<total
    )
    
    return sch.PostListResponse(
        posts=posts,
        pagination=pagination
    )