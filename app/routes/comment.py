from fastapi import Body,HTTPException,status,APIRouter,Depends,Query
from sqlalchemy.orm import Session
from app import oauth2,models,db,schemas as sch
from sqlalchemy import and_

router=APIRouter(tags=['comment'])

@router.post("/comment",status_code=status.HTTP_201_CREATED, response_model=sch.CommentDetailResponse)
def createComment(comment:sch.CommentCreateRequest=Body(...),db:Session=Depends(db.getDb),currentUser: models.User = Depends(oauth2.getCurrentUser)):
    # Check if the post exists
    post = db.query(models.Post).filter(models.Post.id == comment.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {comment.post_id} not found")
    if not post.enable_comments:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"this post has comments disabled")
    # Create the comment
    new_comment =models.Comments(post_id=comment.post_id,user_id=currentUser.id,comment_content=comment.content)
    db.add(new_comment)
    # Update comments_cnt in the Post table
    if post.comments_cnt is None:
        post.comments_cnt =0
    post.comments_cnt += 1
    db.commit()
    db.refresh(new_comment)
    
    # Build proper response
    user = sch.UserBasicResponse(
        id=currentUser.id,
        username=currentUser.username,
        nickname=currentUser.nickname,
        profile_pic=currentUser.profile_picture
    )
    
    return sch.CommentDetailResponse(
        id=new_comment.id,
        post_id=new_comment.post_id,
        content=new_comment.comment_content,
        likes=new_comment.likes,
        created_at=new_comment.created_at,
        user=user
    )

@router.delete("/comments/delete_comment/{comment_id}",status_code=status.HTTP_200_OK, response_model=sch.SuccessResponse)
def deleteComment(comment_id:int,db:Session=Depends(db.getDb),currentUser:models.User=Depends(oauth2.getCurrentUser)):
    commentTodelete=db.query(models.Comments).filter(and_(models.Comments.id==comment_id,models.Comments.user_id==currentUser.id)).first()
    if not commentTodelete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"comment with Id {comment_id} not Found") 
    db.delete(commentTodelete)
    db.commit()
    return sch.SuccessResponse(message=f"Comment {comment_id} deleted successfully")

@router.patch("/comments/edit_comment/{comment_id}",status_code=status.HTTP_200_OK, response_model=sch.CommentDetailResponse)
def editComment(comment_id:int,editInfo:sch.CommentUpdateRequest=Body(...),db:Session=Depends(db.getDb),currentUser:models.User=Depends(oauth2.getCurrentUser)):
    commentToBeEdited=db.query(models.Comments).filter(and_(models.Comments.id==comment_id,models.Comments.user_id==currentUser.id)).first()
    if not commentToBeEdited:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"comment with Id {comment_id} not Found")
    commentToBeEdited.comment_content=editInfo.comment_content
    db.commit()
    db.refresh(commentToBeEdited)
    
    # Build proper response
    user = sch.UserBasicResponse(
        id=currentUser.id,
        username=currentUser.username,
        nickname=currentUser.nickname,
        profile_pic=currentUser.profile_picture
    )
    
    return sch.CommentDetailResponse(
        id=commentToBeEdited.id,
        post_id=commentToBeEdited.post_id,
        content=commentToBeEdited.comment_content,
        likes=commentToBeEdited.likes,
        created_at=commentToBeEdited.created_at,
        user=user
    )

@router.get("/comments-on/{post_id}", response_model=sch.CommentListResponse)
def getAllPosts(post_id:int,
    limit:int=Query(10, ge=1, le=100),
    offset: int = Query(0,ge=0),
    db:Session=Depends(db.getDb),
    currentUser:models.User=Depends(oauth2.getCurrentUser)
    ):
    # calculate the total number of comments on the post
    total=db.query(models.Comments).filter(models.Comments.post_id==post_id).count()
    # only fetch the first 'limit' comments after skipping the first 'offset' comments
    # and order them by the latest as first
    paginatedComments=db.query(models.Comments).filter(models.Comments.post_id==post_id).offset(offset).limit(limit).all()
    
    # Build proper response
    commentsResponse = []
    for comment in paginatedComments:
        user = sch.UserBasicResponse(
            id=comment.user.id,
            username=comment.user.username,
            nickname=comment.user.nickname,
            profile_pic=comment.user.profile_picture
        )
        commentsResponse.append(sch.CommentDetailResponse(
            id=comment.id,
            post_id=comment.post_id,
            content=comment.comment_content,
            likes=comment.likes,
            created_at=comment.created_at,
            user=user
        ))
    
    pagination = sch.PaginationMetadata(
        total=total,
        limit=limit,
        offset=offset,
        has_more=(limit+offset)<total
    )
    
    return sch.CommentListResponse(
        comments=commentsResponse,
        pagination=pagination
    )