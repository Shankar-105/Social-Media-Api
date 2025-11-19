from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends,Query
from app import schemas, models, oauth2,db
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.my_utils.socket_manager import manager
from datetime import datetime


async def reply_msg(
    payload:schemas.ReplyMessageSchema,
    user_id:int,
    db:Session
):    
        # avioiding users from replying to a deleted message
        # obviuosly its impossible to do so as soon after a user deletes a
        # msg obviusly the option's like reply,edit,react or anyother stuff
        # for that message will be removed by the frontend
        # to avoid user replying to a deleted message 
        # but an extra layer of security and a sample demo on how its done
        subq=(
        select(models.DeletedMessage.message_id)
        .where(models.DeletedMessage.user_id == user_id)
        .scalar_subquery()
        )
        original_msg = db.query(models.Message).filter(
             models.Message.id == payload.reply_msg_id,
             models.Message.is_deleted_for_everyone == False,
             ~models.Message.id.in_(subq)).first()
        if not original_msg:
             print("cannot reply to a deleted message")
             return
        # replying for a message is as same as sending a nrmal message
        # with few tweaks in it here we mark the mwessage as is_reply_msg True
        # so that this message will called as a reply msg
        msg = models.Message(
                        content=payload.content,
                        sender_id=user_id,
                        receiver_id=payload.to,
                        is_reply_msg=True,
                        media_type=payload.media_type,
                        media_url=payload.media_url
                    )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        # we store the link reply_msg -> original_msg
        # so that in future while quering the messages
        # and knoiwing that a particular msg is a reply msg
        # we need to know to which msg this is a reply 
        reply_link = models.MessageReplies(
            reply_id=msg.id,
            original_id=payload.reply_msg_id
        )
        db.add(reply_link)
        db.commit()
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
                "is_reply_to_share": False,
                "media_url":msg.media_url,
                "media_type":msg.media_type,
                # original message
                "reply_to": {
                    "msg_id": original_msg.id,
                    "content":  original_msg.content,
                    "sender_name": original_msg.sender.username,
                    "media_url":original_msg.media_url,
                    "media_type":original_msg.media_type,
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
                "is_reply_to_share": False,
                "media_url":msg.media_url,
                "media_type":msg.media_type,
                "reply_to": {
                    "msg_id": original_msg.id,
                    "content":  original_msg.content,
                    "sender_name": original_msg.sender.username,
                    "media_url":original_msg.media_url,
                    "media_type":original_msg.media_type,
                }
        }
        await manager.send_personal_message(payload_to_user,user_id)
        print("Response sent to sender")