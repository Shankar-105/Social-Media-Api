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
    share=db.query(models.SharedPost).filter(
        models.SharedPost.id==share_id,
        models.SharedPost.sender_id==me.id
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

async def delete_share_for_everyone(
    db:Session,
    share_id:int,
    sender_id: int,
    receiver_id: int,
    ):
    print(f"Message ID {share_id} Sender ID {sender_id} Recv ID {receiver_id}")
    share = db.query(models.SharedPost).filter(
        models.SharedPost.id == share_id,
        models.SharedPost.from_user_id == sender_id
    ).first()
    if not share:
        # replaced the exception with return statement so that
        # it doesnt disconnect the user
        print("Message Not Found")
        return
    # Mark as deleted for everyone
    share.is_deleted_for_everyone = True
    db.commit()
    # Notify BOTH users instantly
    payload = {
        "type":"share_deleted",
        "share_id": share_id,
        "is_deleted_for_everyone":True
    }
    print(f"Sender ID {sender_id} Receiver ID {receiver_id}")
    await manager.send_json_to_user(payload,receiver_id)
    await manager.send_personal_message(payload,sender_id)