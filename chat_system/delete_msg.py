from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends,Query,HTTPException
from app import schemas, models, oauth2,db
from sqlalchemy.orm import Session
from app.my_utils.socket_manager import manager
import json,asyncio
from datetime import datetime

router=APIRouter(tags=['delete msg'])

@router.post("/delete/for-me/{msg_id}")
def deleteForMe(
    msg_id: int,
    db: Session=Depends(db.getDb),
    me: models.User = Depends(oauth2.getCurrentUser),
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
    return {"message_id": msg_id, "detail": "Deleted for you"}

async def delete_for_everyone(
    db:Session,
    message_id:int,
    sender_id: int,
    receiver_id: int,
    ):
    print(f"Message ID {message_id} Sender ID {sender_id} Recv ID {receiver_id}")
    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.sender_id == sender_id
    ).first()
    if not message:
        # replaced the exception with return statement so that
        # it doesnt disconnect the user
        print("Message Not Found")
        return
    # Mark as deleted for everyone
    message.is_deleted_for_everyone = True
    db.commit()
    # Notify BOTH users instantly
    payload = {
        "type":"message_deleted",
        "message_id": message_id,
        "is_deleted_for_everyone":True
    }
    print(f"Sender ID {sender_id} Receiver ID {receiver_id}")
    await manager.send_json_to_user(payload,receiver_id)
    await manager.send_personal_message(payload,sender_id)