from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends,Query
from app import schemas, models, oauth2,db
from sqlalchemy.orm import Session
from app.my_utils.websocket import manager
import json
from datetime import datetime
router = APIRouter(prefix="/chat",tags=["chat"])

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: str=Query(None,description="Search query params"),
    db: Session=Depends(db.getDb)
):
    # Validate JWT from query param (or header later)
    if not token:
        await websocket.close(code=1008)
        return
    try:
        current_user = oauth2.getCurrentUser(token,db)
        if current_user.id != user_id:
            await websocket.close(code=1008)
            return
    except:
        await websocket.close(code=1008)
        return
     
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            print("data successfully loaded")
            # Save to DB
            msg = models.Message(
                content=message_data["content"],
                sender_id=user_id,
                receiver_id=message_data["to"]
            )
            db.add(msg)
            db.commit()
            db.refresh(msg)
            print("added to db")
            # Send to receiver if online
            await manager.send_to_user(f"User {user_id}: {msg.content}", msg.receiver_id)
            print("entered into message sender method via send_to_user")
            response_data = {
                "id": msg.id,
                "content": msg.content,
                "sender_id": msg.sender_id,
                "receiver_id": msg.receiver_id,
                "timestamp": msg.created_at.isoformat()  # ← Convert datetime to string
            }
            await manager.send_personal_message(json.dumps(response_data),user_id)
            print("entered into message sender method directly")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(e)
        manager.disconnect(user_id)