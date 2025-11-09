from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends,Query
from app import schemas, models, oauth2,db
from sqlalchemy.orm import Session
from app.my_utils.socket_manager import manager
import json,asyncio
from datetime import datetime

router=APIRouter(tags=['delete msg'])

@router.websocket("/delete-msg/{msg_id}")
async def deleteForMe(
    msg_id: int,
    token: str=Query(None,description="Search query params"),
    db: Session=Depends(db.getDb)
):
    None