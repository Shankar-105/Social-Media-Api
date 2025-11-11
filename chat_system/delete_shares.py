from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends,Query,HTTPException
from app import schemas, models, oauth2,db
from sqlalchemy.orm import Session
from app.my_utils.socket_manager import manager
import json,asyncio
from datetime import datetime

router=APIRouter(tags=['delete share'])

@router.post("/delete-share/for-me/{share_id}")
async def deleteForMe(
    share_id: int,
    db: Session=Depends(db.getDb),
    me: models.User = Depends(oauth2.getCurrentUser),
):
    share=db.query(models.Message).filter(
        models.Message.id==share_id,
        models.Message.sender_id==me.id
    )
    if not share:
        raise HTTPException(status_code=404,detail="Share not found")
    deleted_share=models.DeletedSharedPost(
        user_id=me.id,
        post_id=share_id
    )
    db.add(deleted_share)
    db.commit()
    return {"share_id": share_id, "detail": "Deleted for you"}