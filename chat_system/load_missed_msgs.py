from fastapi import Depends
from app import schemas, models, oauth2,db,config
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
            base_msg = {
                "type": "message",
                "id": m.id,
                "content": m.content,
                "sender_id": m.sender_id,
                "receiver_id": m.receiver_id,
                "media_type":m.media_type if m.media_type != "false" else None,
                "media_url":f"{config.settings.base_url}/chat-media{m.media_url}" if m.media_type != "false" else None,
                "timestamp": m.created_at.isoformat(),
                "is_edited": m.is_edited,
                "reaction_count": m.reaction_cnt,
                "reactions": m.reactions,
                "is_read": m.is_read
            }
            # check whether its a reply message or not
            if m.is_reply_msg:
                # if so then check if its just a reply to a messgage or a post
                if m.is_reply_to_share:
                    shared_post=m.reply_to_shared_post
                    if shared_post:
                        base_msg.update({
                            "is_reply":True,
                            "is_reply_to_share": True,
                            "reply_to": {
                                "share_id":shared_post.id,
                                "content":shared_post.post.media_path,
                                "sender_name":shared_post.from_user.username if shared_post.from_user else "Unknown"
                            }
                        })
                else:
                    original_msg=m.replies_to.original_msg
                    if original_msg:
                        base_msg.update({
                            "is_reply": True,
                            "reply_to": {
                                "msg_id": original_msg.id,
                                "content": original_msg.content,
                                "media_type":m.media_type if original_msg.media_type != "false" else None,
                                "media_url":f"{config.settings.base_url}/chat-media{original_msg.media_url}" if original_msg.media_type != "false" else None,
                                "sender_name": original_msg.sender.username if original_msg.sender else "Unknown"
                            }
                        })
            else:
                base_msg["is_reply"] = False
            missed_content.append(base_msg)

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
                "reactions": s.reactions,
                "sent_at": s.created_at.isoformat(),
                "is_read": s.is_read
            })
        missed_content.sort(key=lambda x : x.get("timestamp") if "timestamp" in  x else x.get("sent_at"))
        return missed_content