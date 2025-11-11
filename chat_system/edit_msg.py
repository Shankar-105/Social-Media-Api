from sqlalchemy.orm import Session
from app import models
from fastapi import APIRouter,Depends
from datetime import datetime
from app import oauth2,db,config
from app.my_utils.socket_manager import manager
from datetime import datetime,timedelta,timezone

router=APIRouter(tags=['can_edit'])

@router.get("/msg/{msg_id}/can_edit")
def can_edit(msg_id:int,db:Session=Depends(db.getDb),currentUser:models.User = Depends(oauth2.getCurrentUser)):
    message = db.query(models.Message).filter(
        models.Message.id == msg_id,
        models.Message.sender_id == currentUser.id
    ).first()
    # almost impossible practically
    # as a user cannot click for an edit over a message that doesnt exist
    if not message:
        return {"message":"message not found"}
    # if the time_difference is greater than 15 mins we say
    # well heyy frontend dont show the edit option by replying
    # the can_edit as false
    # an other major thing to notice is our SQLAlchemy Messages Model
    # is storing the time as a offset-aware datetime object
    # so while here also while subtracting we need to be sure that 
    # the current time we use in calculating the difference is also 
    # a offset-aware datetime object so we do this
    # first create an offset-aware datetime object
    
    curr_time=datetime.now(timezone.utc)
    # and then perform a subtraction
    time_diff = curr_time - message.created_at
    if time_diff > timedelta(minutes=config.settings.max_edit_time):
        return {
            "can_edit":False
        }
    return {
        "can_edit":True
    }
    
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
        # new content is the same old content
        "new_content":message.content,
        "message_id": message_id,
        # is_edited flag is true if its already edited before
        # fasle if not edited before becasue as the user
        # is not changing anything and if it's not edited before 
        # we wouldnt assume that as an edit
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
        "new_content":new_content,
        "message_id": message_id,
        "is_edited":True
    }
    await manager.send_json_to_user(payload,recv_id)
    await manager.send_personal_message(payload,sender_id)