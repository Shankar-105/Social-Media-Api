from fastapi import status,HTTPException,Depends,APIRouter,Form,UploadFile,File
import app.schemas as sch
from typing import Optional
from app import models,oauth2
from app.db import getDb
from sqlalchemy.orm import Session
from sqlalchemy import and_
import os,uuid,shutil
from app.config import settings
router=APIRouter(
    tags=['Posts']
)

# gets a specific post with id -> {postId}
@router.get("/posts/getPost/{postId}", response_model=sch.PostDetailResponse)
def getPost(postId:int,db:Session=Depends(getDb),currentUser:models.User=Depends(oauth2.getCurrentUser)):
    reqPost=db.query(models.Post).filter(and_(models.Post.id==postId,models.Post.user_id==currentUser.id)).first()
    if reqPost==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {postId} not found")
    # is the post viewed before
    isViewed = db.query(models.PostView).filter(
        and_(models.PostView.post_id == postId, models.PostView.user_id == currentUser.id)
    ).first()
    # If no prior view, record the view and increment the count
    if not isViewed:
        # If no prior view, record the view and increment the count
        new_view = models.PostView(post_id=postId,user_id=currentUser.id)
        db.add(new_view)
        reqPost.views+=1
        db.commit()
        db.refresh(reqPost)  # Refresh to get updated post data
    
    # Build proper response with schema
    media_url = None
    if reqPost.media_path:
        media_url = f"{settings.base_url}/{settings.media_folder}/{reqPost.media_path}"
    
    owner = sch.UserBasicResponse(
        id=reqPost.user.id,
        username=reqPost.user.username,
        nickname=reqPost.user.nickname,
        profile_pic=reqPost.user.profile_picture
    )
    
    return sch.PostDetailResponse(
        id=reqPost.id,
        title=reqPost.title,
        content=reqPost.content,
        media_url=media_url,
        media_type=reqPost.media_type,
        likes=reqPost.likes,
        dislikes=reqPost.dis_likes,
        views=reqPost.views,
        comments_count=reqPost.comments_cnt,
        enable_comments=reqPost.enable_comments,
        hashtags=reqPost.hashtags,
        created_at=reqPost.created_at,
        owner=owner
    )


# creates a new post using sqlAlchemy
@router.post("/posts/createPost", status_code=status.HTTP_201_CREATED, response_model=sch.PostDetailResponse)
def create_post(
    title:str=Form(...),
    content:str=Form(...),
    media:Optional[UploadFile]=File(None),  # Optional file
    db: Session=Depends(getDb),
    currentUser:models.User=Depends(oauth2.getCurrentUser) 
):
    # set to None change if uploaded later
    media_path = None
    media_type = None
    if media:
        # ensure the file type is in bounds
        if media.content_type not in ["image/jpeg", "image/png", "video/mp4"]:
            raise HTTPException(400, "Only JPG, PNG, MP4 allowed")
        # Generate unique filename
        # using uuid Universally unique ID which generates a 36 characters
        ext=media.filename.split(".")[-1]
        filename=f"{uuid.uuid4()}.{ext}"
        file_path=os.path.join(settings.media_folder,filename)
        # transfer the data from args to the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(media.file, buffer)
        # we will only store the filename in the db
        media_path=filename
        media_type="image" if media.content_type.startswith("image") else "video"
    new_post = models.Post(
        title=title,
        content=content,
        media_path=media_path,
        media_type=media_type,
        user_id=currentUser.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    # Build proper response
    media_url = None
    if new_post.media_path:
        media_url = f"{settings.base_url}/{settings.media_folder}/{new_post.media_path}"
    
    owner = sch.UserBasicResponse(
        id=currentUser.id,
        username=currentUser.username,
        nickname=currentUser.nickname,
        profile_pic=currentUser.profile_picture
    )
    
    return sch.PostDetailResponse(
        id=new_post.id,
        title=new_post.title,
        content=new_post.content,
        media_url=media_url,
        media_type=new_post.media_type,
        likes=new_post.likes,
        dislikes=new_post.dis_likes,
        views=new_post.views,
        comments_count=new_post.comments_cnt,
        enable_comments=new_post.enable_comments,
        hashtags=new_post.hashtags,
        created_at=new_post.created_at,
        owner=owner
    )
# delets a specific post with the mentioned id -> {id}
@router.delete("/posts/deletePost/{postId}", response_model=sch.SuccessResponse)
def deletePost(postId:int,db:Session=Depends(getDb),currentUser:models.User=Depends(oauth2.getCurrentUser)):
    postToDelete=db.query(models.Post).filter(and_(models.Post.id==postId,models.Post.user_id==currentUser.id)).first()
    if not postToDelete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with Id {postId} not Found")
    # Fix bug: construct path before checking existence
    if postToDelete.media_path:
        media_path = f"{settings.media_folder}/{postToDelete.media_path}"
        if os.path.exists(media_path):
            os.remove(media_path)
    db.delete(postToDelete)
    db.commit()
    return sch.SuccessResponse(message=f"Post {postToDelete.id} deleted successfully")

# update a specific post with id -> {id}
@router.put("/posts/editPost/{postId}", response_model=sch.PostDetailResponse)
def editPost(postId:int,post:sch.PostUpdateRequest,db:Session=Depends(getDb),currentUser:models.User=Depends(oauth2.getCurrentUser)):
    postToUpdate=db.query(models.Post).filter(models.Post.id==postId).first()
    if not postToUpdate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with Id {postId} not Found")
    # from our argument of post we exclude the None values
    # and just pick up the set values and store into a dict update_data
    update_data = post.dict(exclude_unset=True)
    # now we traverse thorugh the update_data and put that data
    # in our postToUpdate
    for key, value in update_data.items():
        setattr(postToUpdate,key,value)
    # commit those updated changes
    db.commit()
    # refresh to qucikly view them below while returing 
    # if not refreshed below returned postToUpdate will be
    # sent as {} to the front End
    db.refresh(postToUpdate)
    
    # Build proper response
    media_url = None
    if postToUpdate.media_path:
        media_url = f"{settings.base_url}/{settings.media_folder}/{postToUpdate.media_path}"
    
    owner = sch.UserBasicResponse(
        id=postToUpdate.user.id,
        username=postToUpdate.user.username,
        nickname=postToUpdate.user.nickname,
        profile_pic=postToUpdate.user.profile_picture
    )
    
    return sch.PostDetailResponse(
        id=postToUpdate.id,
        title=postToUpdate.title,
        content=postToUpdate.content,
        media_url=media_url,
        media_type=postToUpdate.media_type,
        likes=postToUpdate.likes,
        dislikes=postToUpdate.dis_likes,
        views=postToUpdate.views,
        comments_count=postToUpdate.comments_cnt,
        enable_comments=postToUpdate.enable_comments,
        hashtags=postToUpdate.hashtags,
        created_at=postToUpdate.created_at,
        owner=owner
    )