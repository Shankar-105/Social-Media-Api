from sqlalchemy.orm import Session
from app import models
from datetime import datetime
from app.my_utils.socket_manager import manager
async def edit_message(db:Session,message_id:int,new_content:str,sender_id:int,recv_id:int):
    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.sender_id == sender_id  # Only sender can edit
    ).first()

    if not message:
        return None
    # Don't update if content is same
    if message.content.strip() == new_content:
        # No change
        payload = {
        "type":"edited_msg",
        "message_id": message_id,
        "is_edited":False if not message.is_edited else True
    }
        await manager.send_json_to_user(payload,recv_id)
        await manager.send_personal_message(payload,sender_id)
        return
    # Update content and flags
    message.content = new_content
    message.is_edited = True
    message.edited_at = datetime.utcnow()
    db.commit()
    db.refresh(message)
    payload = {
        "type":"edited_msg",
        "message_id": message_id,
        "new_content":new_content,
        "is_edited":True
    }
    await manager.send_json_to_user(payload,recv_id)
    await manager.send_personal_message(payload,sender_id)