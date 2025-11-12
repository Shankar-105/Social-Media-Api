from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends,Query
from app import schemas, models, oauth2,db
from sqlalchemy.orm import Session
from app.my_utils.socket_manager import manager
from datetime import datetime

async def react(
    reaction:schemas.ReactionPayload,
    user_id: int,
    db: Session
): 
    msg = db.query(models.Message).filter(models.Message.id == reaction.message_id).first()
    if not msg:
        return None
    
    # Update reaction
    old_reaction = msg.reaction
    # if user reacted with the same rection then remove the reaction
    # else add that new reaction to the msg.reaction
    msg.reaction = reaction.reaction if old_reaction != reaction.reaction else None
    db.commit()

    # payload
    payload = {
        "type": "reaction_update",
        "data": {
            "message_id": msg.id,
            "reaction": msg.reaction if msg.reaction else "removed",
            "reacted_by": user_id
        }
    }
    # Send to BOTH sender and receiver
    await manager.send_personal_message(payload,msg.sender_id)
    await manager.send_json_to_user(payload,msg.receiver_id)