from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime
from app.my_utils.socket_manager import manager

async def mark_as_read(payload: dict, reader_id: int, db: Session):
    try:
        sender_id = int(payload.get("sender_id"))
        # We might want to mark *all* messages from this sender to me as read, or just specific ones.
        # Instagram usually marks the conversation as read.
        # Let's mark all unread messages from this sender to the current user (reader) as read.
        
        unread_messages = db.query(models.Message).filter(
            models.Message.sender_id == sender_id,
            models.Message.receiver_id == reader_id,
            models.Message.is_read == False
        ).all()
        
        if not unread_messages:
            return

        now = datetime.utcnow()
        for msg in unread_messages:
            msg.is_read = True
            msg.read_at = now
        
        db.commit()
        
        # Notify the sender (the one who sent the messages) that they have been read
        # We send a "read_receipt" event to the sender_id
        await manager.send_personal_message(
            {
                "type": "read_receipt",
                "reader_id": reader_id,
                "read_at": str(now),
                "conversation_with": reader_id # context for the sender
            },
            sender_id
        )
        
    except Exception as e:
        print(f"Error in read_receipt: {e}")
