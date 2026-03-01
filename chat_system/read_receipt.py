from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app import models, schemas
from datetime import datetime
from app.my_utils.socket_manager import manager

async def mark_as_read(payload: dict, reader_id: int, db: AsyncSession):
    try:
        sender_id = int(payload.get("sender_id"))
        
        # Find all unread messages from this sender to the current user (reader)
        result = await db.execute(
            select(models.Message).where(
                models.Message.sender_id == sender_id,
                models.Message.receiver_id == reader_id,
                models.Message.is_read == False
            )
        )
        unread_messages = result.scalars().all()
        
        if not unread_messages:
            return

        now = datetime.utcnow()
        # Bulk update using an UPDATE statement
        await db.execute(
            update(models.Message)
            .where(
                models.Message.sender_id == sender_id,
                models.Message.receiver_id == reader_id,
                models.Message.is_read == False
            )
            .values(is_read=True, read_at=now)
        )
        await db.commit()
        
        # Notify the sender that their messages have been read
        await manager.send_personal_message(
            {
                "type": "read_receipt",
                "reader_id": reader_id,
                "read_at": str(now),
                "conversation_with": reader_id
            },
            sender_id
        )
        
    except Exception as e:
        print(f"Error in read_receipt: {e}")
