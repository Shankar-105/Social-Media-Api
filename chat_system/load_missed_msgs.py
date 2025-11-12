from fastapi import Depends
from app import schemas, models, oauth2,db
from sqlalchemy.orm import Session
from app.my_utils.socket_manager import manager
from datetime import datetime

async def load_missed_content(
    user_id: int,
    db: Session=Depends(db.getDb)
):
        missed_messages = db.query(models.Message).filter(
                models.Message.is_deleted_for_everyone==False,
                models.Message.receiver_id == user_id,
                models.Message.is_read == False
            ).order_by(models.Message.created_at.asc()).all()

        if missed_messages:
            db.query(models.Message).filter(
                models.Message.is_deleted_for_everyone==False,
                models.Message.receiver_id == user_id,
                models.Message.is_read == False
            ).update({"is_read":True,"read_at":datetime.utcnow()},synchronize_session=False)
            db.commit()

        missed_shares = db.query(models.SharedPost).filter(
        models.SharedPost.to_user_id == user_id,
        models.SharedPost.is_read == False
    ).order_by(models.SharedPost.created_at.asc()).all()
        
        if missed_shares:
                db.query(models.SharedPost).filter(
                    models.SharedPost.to_user_id == user_id,
                    models.SharedPost.is_read == False
                ).update({"is_read": True}, synchronize_session=False)
                db.commit()

        missed_content=[]
        for m in missed_messages:
            missed_content.append({
                "type": "message",
                "id": m.id,
                "content": m.content,
                "sender_id": m.sender_id,
                "receiver_id":m.receiver_id,
                "is_edited" : m.is_edited,
                "timestamp": m.created_at.isoformat(),
                "is_read": m.is_read
            })

        for s in missed_shares:
            missed_content.append({
                "type": "shared_post",
                "shared_id": s.id,
                "post_id": s.post.id,
                "sender_id": s.from_user_id,
                "receiver_id":s.to_user_id,
                "title": (s.post.title or "")[:60],
                "media_type": s.post.media_type,
                "media_url": s.post.media_path,
                "sender_nickname": s.from_user.nickname,
                "caption_message": s.message,
                "sent_at": s.created_at.isoformat(),
                "is_read": s.is_read
            })
        missed_content.sort(key=lambda x : x.get("timestamp") if "timestamp" in  x else x.get("sent_at"))
        return missed_content