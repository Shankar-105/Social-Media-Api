from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models,oauth2,db
from app.my_utils.time_formatting import format_timestamp

router = APIRouter(tags=['Message Info'])

@router.get("/msgs/{msg_id}/info")
def get_message_info(
    msg_id: int,
    db: Session = Depends(db.getDb),
    currentUser: models.User = Depends(oauth2.getCurrentUser)
):
    msg = db.query(models.Message).filter(models.Message.id == msg_id).first()
    if not msg:
        raise HTTPException(404, "Message not found")
    
    # Only sender or receiver can see info
    if msg.sender_id != currentUser.id and msg.receiver_id != currentUser.id:
        raise HTTPException(403,"Not authorized")
    # simple message information
    return {
        "message_id": msg.id,
        "delivered_at": format_timestamp(msg.created_at),
        "read_at": format_timestamp(msg.read_at) if msg.read_at else None,
        "is_read": msg.is_read
    }