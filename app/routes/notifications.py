from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
import app.schemas as sch
from app import models, db, oauth2
from app import notification_service as ns

router = APIRouter(tags=["notifications"])

@router.get(
    "/me/notifications",
    status_code=status.HTTP_200_OK,
    response_model=sch.NotificationListResponse,
)

async def get_my_notifications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db_session: AsyncSession = Depends(db.getDb),
    current_user: models.User = Depends(oauth2.getCurrentUser),
):
    """Return paginated notifications for the authenticated user, newest first."""
    notifications = await ns.get_notifications(db_session, current_user.id, limit, offset)
    unread_count = await ns.get_unread_count(db_session, current_user.id)

    total_result = await db_session.execute(
        select(func.count())
        .select_from(models.Notification)
        .where(models.Notification.owner_id == current_user.id)
    )
    total = total_result.scalar() or 0

    return sch.NotificationListResponse(
        notifications=notifications,
        unread_count=unread_count,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total,
    )


@router.get(
    "/me/notifications/unread-count",
    status_code=status.HTTP_200_OK,
    response_model=sch.UnreadCountResponse,
)

async def get_unread_notification_count(
    db_session: AsyncSession = Depends(db.getDb),
    current_user: models.User = Depends(oauth2.getCurrentUser),
):
    """Return the unread notification count — used for the badge number in the UI."""
    count = await ns.get_unread_count(db_session, current_user.id)
    return sch.UnreadCountResponse(count=count)


@router.patch(
    "/me/notifications/read",
    status_code=status.HTTP_200_OK,
    response_model=sch.SuccessResponse,
)
async def mark_all_notifications_read(
    db_session: AsyncSession = Depends(db.getDb),
    current_user: models.User = Depends(oauth2.getCurrentUser),
):
    """Mark every unread notification for the current user as read."""
    await ns.mark_all_read(db_session, current_user.id)
    return sch.SuccessResponse(message="All notifications marked as read")
