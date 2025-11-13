from fastapi import APIRouter, HTTPException ,Depends
from app import schemas, models, oauth2,db
from sqlalchemy.orm import Session
from app.my_utils.socket_manager import manager
from datetime import datetime

router=APIRouter(tags=['msg reactions'])

async def react(
    reaction:schemas.ReactionPayload,
    user_id:int,
    db: Session
): 
    the_msg=db.query(models.Message).filter(models.Message.id == reaction.message_id).first()
    elgibile=[the_msg.sender_id,the_msg.receiver_id]
    print(user_id,elgibile)
    if user_id not in elgibile:
        print("working")
        return {
            "status":"Unknown User"
        }
    msg = db.query(models.MessageReaction).filter(models.MessageReaction.message_id == reaction.message_id,models.MessageReaction.user_id == user_id).first()
    # if there's no such record in MessageReaction Table
    # then this is the first new reaction by the user with id as user_id 
    # so create a MessageReaction object and add it to that tble
    if not msg:
        new_reaction=models.MessageReaction(message_id=reaction.message_id,user_id=user_id,reaction=reaction.reaction)
        db.add(new_reaction)
        the_msg.reaction_cnt+=1
    # the msg reaction already exists in that tbale but the
    # user has again sent the same reaction well then remove it 
    elif msg and msg.reaction == reaction.reaction:
        db.delete(msg.reaction)
        the_msg.reaction_cnt-=1
    # msg exists and the new reation isnt the old one
    # well then he sent a brand new reaciton just change it
    else:
        msg.reaction=reaction.reaction
    # any changes commit thehm off
    db.commit()
    
    # payload
    payload = {
        "type": "reaction_update",
        "data": {
            "message_id": the_msg.id,
            "reaction": msg.reaction if msg.reaction else "removed",
            "reaction_count":the_msg.reaction_cnt,
            "reacted_by": user_id
        }
    }
    # Send to BOTH sender and receiver
    await manager.send_personal_message(payload,the_msg.sender_id)
    await manager.send_json_to_user(payload,the_msg.receiver_id)