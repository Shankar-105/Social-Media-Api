from fastapi import APIRouter,Depends
from app import schemas, models, oauth2, db
from sqlalchemy.orm import Session
from app.my_utils.socket_manager import manager
from typing import List

router = APIRouter(tags=['shared post reactions'])

# same as the message_reaction but here the shares are
# stored in the SharedPosts table so we query that insted of
# the messages table
@router.get("/shared/{shared_id}/reactions", response_model=List[schemas.ReactedUsers])
def get_shared_post_reactions(
    shared_id: int,
    db: Session = Depends(db.getDb),
    currentUser: models.User = Depends(oauth2.getCurrentUser)
):
    shared = db.query(models.SharedPost).filter(models.SharedPost.id == shared_id).first()
    if not shared:
        print("NO Such POst found")
        return
    if shared.from_user_id != currentUser.id and shared.to_user_id != currentUser.id:
        print("UNknown User")
        return

    reactions = (
        db.query(models.SharedPostReaction)
        .filter(models.SharedPostReaction.shared_post_id == shared_id)
        .all()
    )
    return [
        {
            "user_id": r.user.id,
            "username": r.user.username,
            "profile_pic": r.user.profile_picture,
            "reaction": r.reaction
        }
        for r in reactions
    ]

async def react_to_shared_post(
    reaction: schemas.ReactionPayload,
    user_id: int,
    db: Session
):
    global isNewRecord
    # message_id is nothing but share_id
    shared = db.query(models.SharedPost).filter(models.SharedPost.id == reaction.message_id).first()
    if not shared:
        return {"status": "not found"}

    eligible = [shared.from_user_id, shared.to_user_id]

    if user_id not in eligible:
        print("unauth guy")
        return {"status": "unauthorized"}

    existing = db.query(models.SharedPostReaction).filter(
        models.SharedPostReaction.shared_post_id == reaction.message_id,
        models.SharedPostReaction.user_id == user_id
    ).first()

    if not existing:
        isNewRecord=True
        # New reaction
        new_reaction = models.SharedPostReaction(
            shared_post_id=reaction.message_id,
            user_id=user_id,
            reaction=reaction.reaction
        )
        db.add(new_reaction)
        shared.reaction_cnt+=1
    elif existing.reaction == reaction.reaction:
        isNewRecord=False
        # Toggle off
        db.delete(existing)
        shared.reaction_cnt-=1
    else:
        isNewRecord=True
        # Change reaction
        existing.reaction = reaction.reaction
    # commit any change
    db.commit()
    
    payload = {
        "type": "reaction_update",
        "data": {
            "message_id":shared.id,
            "reaction": reaction.reaction if isNewRecord else None,
            "reaction_count":shared.reaction_cnt,
            "reacted_by": user_id
        }
    }

    # Send to BOTH users
    await manager.send_personal_message(payload,shared.from_user_id)
    await manager.send_json_to_user(payload,shared.to_user_id)