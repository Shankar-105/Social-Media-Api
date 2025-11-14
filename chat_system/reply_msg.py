from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends,Query
from app import schemas, models, oauth2,db
from sqlalchemy.orm import Session
from app.my_utils.socket_manager import manager
from chat_system import delete_msg,delete_shares,edit_msg,load_missed_msgs,msg_reaction,share_reaction
import json,asyncio
from datetime import datetime


async def reply_msg(
    payload:schemas.ReplyMessageSchema,
    user_id:int,
    db:Session
):
        msg = models.Message(
                        content=payload.content,
                        sender_id=user_id,
                        receiver_id=payload.to
                    )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        print("added to db")
        # Check if receiver is in active_connections
        receiver_id = msg.receiver_id
        original_msg = db.query(models.Message).filter(models.Message.id == payload.reply_msg_id).first()
        if receiver_id in manager.active_connections:
            try:
                reply_message_payload={
                "id": msg.id,
                "content": msg.content,
                "sender_id": user_id,
                "timestamp": msg.created_at.isoformat(),
                "is_reply": True,
                "reply_to": {
                    "msg_id": original_msg.id,
                    "content":  original_msg.content,
                    "sender_name": original_msg.sender.username
                }
        }
                # Try to send (if fails, it's a zombie)
                await manager.send_json_to_user(reply_message_payload,
                    receiver_id
                )
                print("Message sent via WebSocket")
                msg.is_read = True
                msg.read_at=datetime.utcnow()
                db.commit()
                print(f"Message {msg.id} marked as READ")
            except Exception as e:
                # Send failed → zombie socket → remove
                print(f"Send failed: {e}")
                manager.disconnect(receiver_id)
                # TODO: Later, send push notification here
        else:
            # Offline → don't send, just save in DB
            print("Receiver offline — message saved in DB")
            # TODO: Later, send push notification here
        # Send response back to sender
        payload_to_user={
                "id": msg.id,
                "content": msg.content,
                "sender_id": user_id,
                "timestamp": msg.created_at.isoformat(),
                "is_reply": True,
                "reply_to": {
                    "msg_id": original_msg.id,
                    "content":  original_msg.content,
                    "sender_name": original_msg.sender.username
                }
        }
        await manager.send_personal_message(payload_to_user,user_id)
        print("Response sent to sender")