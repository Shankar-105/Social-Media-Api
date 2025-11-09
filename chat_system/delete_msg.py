from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends,Query,HTTPException
from app import schemas, models, oauth2,db
from sqlalchemy.orm import Session
from app.my_utils.socket_manager import manager
import json,asyncio
from datetime import datetime

router=APIRouter(tags=['delete msg'])

@router.post("/delete/for-me/{msg_id}")
async def deleteForMe(
    msg_id: int,
    token: str=Query(None,description="Search query params"),
    db: Session=Depends(db.getDb),
    me: models.UniqueConstraint = Depends(oauth2.getCurrentUser),
):
    message=db.query(models.Message).filter(
        models.Message.id==msg_id,
        models.Message.sender_id==me.id
    )
    if not message:
        raise HTTPException(status_code=404,detail="Message not found")
    deleted_msg=models.DeletedMessage(
        user_id=me.id,
        message_id=msg_id
    )
    db.add(deleted_msg)
    db.commit()
    db.refresh(deleted_msg)
    return {"message_id": msg_id, "detail": "Deleted for you"}