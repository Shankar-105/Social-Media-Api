# routes/share.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.db import getDb
from app.models import SharedPost, Post, User
from app.schemas import SharePostCreate,SharedPostResponse
from app.oauth2 import getCurrentUser
from app.my_utils.socket_manager import manager  # your WebSocket ConnectionManager
import json

router = APIRouter(tags=["Share Post"])

@router.post("/share",response_model=SharedPostResponse)
async def share_post(
    payload: SharePostCreate,
    db: Session = Depends(getDb),
    me: User = Depends(getCurrentUser),
):
    """
    1. Validate post exists
    2. Validate receiver exists & not self
    3. Save SharedPost record
    4. Push a **preview** to receiver via WebSocket (if online)
    5. Return the DB record (for sender UI)
    """
    post:Post = (
        db.query(Post)      # get owner nickname
        .filter(Post.id == payload.post_id)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    receiver: User = db.query(User).filter(User.id == payload.to_user_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    if receiver.id == me.id:
        raise HTTPException(status_code=400, detail="Cannot share with yourself")

    shared = SharedPost(
        post_id=payload.post_id,
        from_user_id=me.id,
        to_user_id=receiver.id,
        message=payload.message,
    )
    db.add(shared)
    db.commit()
    db.refresh(shared)

    preview = {
        "type": "shared_post",
        "shared_id": shared.id,
        "post_id": post.id,
        "title": (post.title or "")[:60] + ("..." if post.title and len(post.title) > 60 else ""),
        "media_type": post.media_type,          
        "media_url": post.media_path,       
        "owner_nickname": post.user.nickname,
        "sender_nickname": me.nickname,
        "message": payload.message or f"{me.nickname} shared a post with you!",
        "sent_at": shared.created_at.isoformat(),
    }
    if receiver.id in manager.active_connections:
        try:
            await manager.send_personal_message(json.dumps(preview), receiver.id)
            # Mark as read immediately if delivered
            shared.is_read = True
            db.commit()
        except:
            pass  # Offline or error → stays unread
    return shared