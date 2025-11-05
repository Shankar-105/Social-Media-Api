from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends,Query
from app import schemas, models, oauth2,db
from sqlalchemy.orm import Session
from app.my_utils.socket_manager import manager
import json,asyncio
from datetime import datetime
router = APIRouter(tags=["chat"])

ping_task=None

@router.websocket("/chat/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: str=Query(None,description="Search query params"),
    db: Session=Depends(db.getDb)
):
    # we check whether the token is sent or not 
    # if not sent then we close the socket connection 
    # because we require token to validate or authunicate the user
    if not token:
        await websocket.close(code=1008)
        return
    try:
        # get the user from the token passed token
        current_user = oauth2.getCurrentUser(token,db)
        # if he is a different guy well then close the socket connection
        # this prevents spoofing other users acccessing or pretending to be the actual user
        if current_user.id != user_id:
            await websocket.close(code=1008)
            return
    except:
        await websocket.close(code=1008)
        return
    # well if the token has passed all the above tests
    # make a connection request by using the manager obj 
    await manager.connect(user_id,websocket)
    global ping_task
    if ping_task is None:
        ping_task = asyncio.create_task(manager.periodic_ping())
        print("Security guard started — pinging every 20 sec")
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            if message_data.get("type") == "pong":
                print("Pong received — user alive")
                continue  # Skip to next message
            
            # Save to DB (ALWAYS — even if offline)
            msg = models.Message(
                content=message_data["content"],
                sender_id=user_id,
                receiver_id=message_data["to"]
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
                "timestamp": msg.created_at.isoformat()
            }
            await manager.send_personal_message(response_data, user_id)
            print("Response sent to sender")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(e)
        manager.disconnect(user_id)