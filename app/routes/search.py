from fastapi import HTTPException,status,Body,APIRouter,Depends,Request,Query
from app import models,db,schemas as sch,oauth2,config
from sqlalchemy.orm import Session
from typing import Annotated
router=APIRouter(tags=['search'])

@router.get("/search", status_code=status.HTTP_202_ACCEPTED, response_model=sch.SearchResultResponse)
def search(searchParams: sch.SearchRequest = Depends(), db: Session = Depends(db.getDb), currenUser: models.User = Depends(oauth2.getCurrentUser)):
    if searchParams.q and searchParams.q.startswith("#"):
        # Hashtag search - search for posts
        hashtag = searchParams.q.lstrip("#")
        queryResult=db.query(models.Post).filter(models.Post.hashtags.ilike(f"%{hashtag}%"))
        if searchParams.orderBy == "likes":
            queryResult=queryResult.order_by(models.Post.likes.desc())
        queryResult=queryResult.order_by(models.Post.created_at.asc())
        total = queryResult.count()
        resPosts=queryResult.offset(searchParams.offset).limit(searchParams.limit).all()
        
        # Build proper response for posts
        posts = []
        for post in resPosts:
            posts.append(sch.PostListItemResponse(
                id=post.id,
                title=post.title,
                media_url=f"{config.settings.base_url}/{config.settings.media_folder}/{post.media_path}" if post.media_path else None,
                media_type=post.media_type,
                likes=post.likes,
                comments_count=post.comments_cnt,
                created_at=post.created_at
            ))
        
        return sch.SearchResultResponse(
            result_type="posts",
            posts=posts,
            total=total
        )
    elif searchParams.q:
        # Username search - search for users
        resUsers=(
            db.query(models.User)
            .filter(models.User.username.ilike(f"%{searchParams.q}%"))
            .offset(searchParams.offset)
            .limit(searchParams.limit)
            .all()
        )
        total = db.query(models.User).filter(models.User.username.ilike(f"%{searchParams.q}%")).count()
        
        # Build proper response for users
        users = []
        for user in resUsers:
            users.append(sch.UserBasicResponse(
                id=user.id,
                username=user.username,
                nickname=user.nickname,
                profile_pic=user.profile_picture
            ))
        
        return sch.SearchResultResponse(
            result_type="users",
            users=users,
            total=total
        )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Query Parameters Required")