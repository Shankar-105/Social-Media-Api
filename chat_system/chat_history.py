
from fastapi import status,HTTPException,Depends,Body,APIRouter
import app.schemas as sch
from app import models,oauth2
from app.db import getDb
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import IntegrityError

router = APIRouter(tags=["chat_history"])

@router.get("/history/{friend_id}",response_model=List[sch.ChatHistory])
def get_chat_history(
    friend_id: int,
    db: Session = Depends(getDb),
    currentUser: models.User = Depends(oauth2.getCurrentUser),
):
    if friend_id == currentUser.id:
        raise HTTPException(status_code=400, detail="Cannot chat with yourself")

    # CRITICAL: Hide undelivered messages from friend
    messages = db.query(models.Message).filter(
        (
            # My messages show all whether he has seen them or not
            (models.Message.sender_id == currentUser.id) &
            (models.Message.receiver_id == friend_id)
        ) | (
            # Friend's messages only show delivered msgs is_read -> True
            (models.Message.sender_id == friend_id) &
            (models.Message.receiver_id == currentUser.id) &
            (models.Message.is_read == True)
        )
    ).order_by(models.Message.created_at.desc())
    messages=messages[::-1]
    return messages  # oldest first