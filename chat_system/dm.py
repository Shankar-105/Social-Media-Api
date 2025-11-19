from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends,Query
from app import schemas, models, oauth2,db
from sqlalchemy.orm import Session
from app.my_utils.socket_manager import manager
import json,asyncio
from datetime import datetime
               
async def messageUser(
    payload:schemas.MessageSchema,
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
        if receiver_id in manager.active_connections:
            try:
                # Try to send (if fails, it's a zombie)
                await manager.send_to_user(
                    f"User {user_id}: {msg.content}", 
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
        response_data = {
            "id": msg.id,
            "content": msg.content,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "timestamp": msg.created_at.isoformat(),
            "is_read":msg.is_read
        }
        await manager.send_personal_message(response_data, user_id)
        print("Response sent to sender")