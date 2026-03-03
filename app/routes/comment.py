from fastapi import Body,HTTPException,status,APIRouter,Depends,Query,BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,func
from app import oauth2,models,db,schemas as sch
from app.notification_service import create_notification
from app.models import NotificationType

router=APIRouter(tags=['comment'])

@router.post("/comment",status_code=status.HTTP_201_CREATED, response_model=sch.CommentDetailResponse)
async def createComment(comment:sch.CommentCreateRequest=Body(...),db:AsyncSession=Depends(db.getDb),currentUser: models.User = Depends(oauth2.getCurrentUser),background_tasks:BackgroundTasks=BackgroundTasks()):
    # Check if the post exists
    result = await db.execute(select(models.Post).where(models.Post.id == comment.post_id))
    post = result.scalars().first()
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
    await db.commit()
    await db.refresh(new_comment)
    # Notify the post owner when someone comments on their post.
    # Guard: no self-notification if the post owner comments on their own post.
    if currentUser.id != post.user_id:
        background_tasks.add_task(
            create_notification,
            actor_id=currentUser.id,
            owner_id=post.user_id,
            notif_type=NotificationType.comment,
            actor_username=currentUser.username,
            entity_id=comment.post_id,
            entity_type="post",
        )
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
async def deleteComment(comment_id:int,db:AsyncSession=Depends(db.getDb),currentUser:models.User=Depends(oauth2.getCurrentUser)):
    result=await db.execute(select(models.Comments).where(and_(models.Comments.id==comment_id,models.Comments.user_id==currentUser.id)))
    commentTodelete=result.scalars().first()
    if not commentTodelete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"comment with Id {comment_id} not Found") 
    await db.delete(commentTodelete)
    await db.commit()
    return sch.SuccessResponse(message=f"Comment {comment_id} deleted successfully")

@router.patch("/comments/edit_comment/{comment_id}",status_code=status.HTTP_200_OK, response_model=sch.CommentDetailResponse)
async def editComment(comment_id:int,editInfo:sch.CommentUpdateRequest=Body(...),db:AsyncSession=Depends(db.getDb),currentUser:models.User=Depends(oauth2.getCurrentUser)):
    result=await db.execute(select(models.Comments).where(and_(models.Comments.id==comment_id,models.Comments.user_id==currentUser.id)))
    commentToBeEdited=result.scalars().first()
    if not commentToBeEdited:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"comment with Id {comment_id} not Found")
    commentToBeEdited.comment_content=editInfo.comment_content
    await db.commit()
    await db.refresh(commentToBeEdited)
    
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
async def getAllPosts(post_id:int,
    limit:int=Query(10, ge=1, le=100),
    offset: int = Query(0,ge=0),
    db:AsyncSession=Depends(db.getDb),
    currentUser:models.User=Depends(oauth2.getCurrentUser)
    ):
    # calculate the total number of comments on the post
    countResult=await db.execute(select(func.count()).select_from(models.Comments).where(models.Comments.post_id==post_id))
    total=countResult.scalar()
    # only fetch the first 'limit' comments after skipping the first 'offset' comments
    # and order them by the latest as first
    commentsResult=await db.execute(select(models.Comments).where(models.Comments.post_id==post_id).offset(offset).limit(limit))
    paginatedComments=commentsResult.scalars().all()
    
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