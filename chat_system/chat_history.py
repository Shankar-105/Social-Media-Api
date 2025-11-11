
from fastapi import status,HTTPException,Depends,Body,APIRouter
import app.schemas as sch
from app import models,oauth2
from app.db import getDb
from sqlalchemy.orm import Session
from sqlalchemy import or_,and_,select
from typing import List
from sqlalchemy.exc import IntegrityError

router = APIRouter(tags=["chat_history"])

@router.get("/history/{friend_id}")
def get_chat_history(
    friend_id: int,
    db: Session = Depends(getDb),
    currentUser: models.User = Depends(oauth2.getCurrentUser),
):
    if friend_id == currentUser.id:
        raise HTTPException(status_code=400, detail="Cannot chat with yourself")

    # CRITICAL: Hide undelivered messages from friend
    # firstly let us fetch out the 'delted for me' msgs by the current user
    subq=(
        # to avoid the SAWaring we need put the subQuery inside the select() constructor
        select(models.DeletedMessage.message_id)
        .where(models.DeletedMessage.user_id == currentUser.id)
        .scalar_subquery()  # imp  because we are using this sub-query inside the in_ 
        # so we need to ensure not all the cols are passed but that one required column
        # which is also clearly mentioned in the select() the 'message_id'
    )
    # now let us use that subquery in NOT EXISTS and simply query off the final messages
    messages = db.query(models.Message).filter(
        # 1. Not deleted for everyone
        models.Message.is_deleted_for_everyone == False,
        # 2. Is between these two users
        or_(
            # show everything from sender side even if read or not
            and_(models.Message.sender_id == currentUser.id, models.Message.receiver_id == friend_id),
            # from receiver side show only the messages which are actually delivered
            and_(models.Message.sender_id == friend_id, models.Message.receiver_id == currentUser.id,
                 models.Message.is_read == True)
        ),
        # 3. Not deleted by THIS user (NOT EXISTS)
        ~models.Message.id.in_(subq)
    ).order_by(models.Message.created_at.desc()).all()
    # shared posts

    deleted_shared_subq = (
    select(models.DeletedSharedPost.shared_post_id)
    .where(models.DeletedSharedPost.user_id == currentUser.id)
    .scalar_subquery()
)
    shared_posts = db.query(models.SharedPost).filter(
        models.SharedPost.is_deleted_for_everyone == False,
        (
            # My messages show all whether he has seen them or not
            (models.SharedPost.from_user_id == currentUser.id) &
            (models.SharedPost.to_user_id == friend_id)
        ) | (
            # Friend's messages only show delivered msgs is_read -> True
            (models.SharedPost.from_user_id == friend_id) &
            (models.SharedPost.to_user_id == currentUser.id) &
            (models.SharedPost.is_read == True)
        ),(
        ~models.SharedPost.id.in_(deleted_shared_subq)    
        )
    ).order_by(models.SharedPost.created_at.desc()).all()

    chat_history=[]
    for m in messages:
        chat_history.append({
            "type": "message",
            "id": m.id,
            "content": m.content,
            "sender_id": m.sender_id,
            "receiver_id":m.receiver_id,
            "timestamp": m.created_at.isoformat(),
            "is_read": m.is_read
        })

    for s in shared_posts:
        chat_history.append({
            "type": "shared_post",
            "shared_id": s.id,
            "post_id": s.post.id,
            "sender_id": s.from_user_id,
            "receiver_id":s.to_user_id,
            "title": (s.post.title or "")[:60],
            "media_type": s.post.media_type,
            "media_url": s.post.media_path,
            "sender_nickname": s.from_user.nickname,
            "message": s.message,
            "sent_at": s.created_at.isoformat(),
            "is_read": s.is_read
        })
    chat_history.sort(key=lambda x : x.get("timestamp") if "timestamp" in  x else x.get("sent_at"))
    for x in chat_history:
        print(x.get("timestamp") if "timestamp" in  x else x.get("sent_at"))
    return chat_history  # oldest first