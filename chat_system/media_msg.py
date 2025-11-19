# routes/dm.py or routes/chat.py
from fastapi import File, UploadFile, APIRouter, Depends
import shutil
import os
from datetime import datetime
from uuid import uuid4
from app import models,oauth2,schemas
from sqlalchemy.orm import Session
from app.my_utils.socket_manager import manager
router = APIRouter()

@router.post("/upload-media")
async def upload_media(
    file:UploadFile = File(...),
    current_user = Depends(oauth2.getCurrentUser)
):
    # get the file type using the content_type attribute of the fastapi UploadFile class
    media_type = file.content_type.split("/")[0]  # 'video', 'audio', 'image'
    folder = f"chat-media/{media_type}s"  # media/videos, media/audios
    # create the dir if dosnt exist
    os.makedirs(folder,exist_ok=True)

    # Secure filename using uuid4
    file_extension = file.filename.split(".")[-1]
    filename = f"{uuid4()}.{file_extension}"
    file_path = f"{folder}/{filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Return media URL to frontend
    media_url = f"/{media_type}s/{filename}"
    return {"media_url":media_url,"type":media_type}

async def sendMediaMsg(
    payload:schemas.MediaTypeMessage,
    user_id:int,
    db: Session
):
    # Create the media type message
    mediaMsg = models.Message(
        content=payload.content,
        sender_id=user_id,
        receiver_id=payload.to,
        media_type=payload.media_type,
        media_url=payload.media_url
    )
    db.add(mediaMsg)
    db.commit()
    db.refresh(mediaMsg)

    reply_payload = {
        "id": mediaMsg.id,
        "content": mediaMsg.content,
        "media_url":mediaMsg.media_url,
        "media_type":mediaMsg.media_type,
        "sender_id": user_id,
        "timestamp": mediaMsg.created_at.isoformat(),
        "is_reply": False,
        "is_reply_to_share": False,
    }

    # Send to receiver (same logic as before)
    if payload.to in manager.active_connections:
        try:
            await manager.send_json_to_user(reply_payload,payload.to)
            mediaMsg.is_read = True
            mediaMsg.read_at = datetime.utcnow()
            db.commit()
        except:
            manager.disconnect(payload.to)
    # Send back to sender
    await manager.send_personal_message(reply_payload,user_id)