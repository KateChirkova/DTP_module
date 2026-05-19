import logging

from fastapi import APIRouter, Depends, HTTPException, Query

logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session

from src.traffic_dtp.api.deps import get_current_user
from src.traffic_dtp.db.models import Notification, User
from src.traffic_dtp.db.session import get_db
from src.traffic_dtp.services.notifications import (
    active_notifications_query,
    mark_all_notifications_read,
    mark_notification_read,
    push_unread_count_ws,
    status_for_user,
    unread_count_for_user,
)
from src.traffic_dtp.services.ws_manager import manager

# общие уведомления; прочтение per-user в notification_reads
router = APIRouter(prefix="/api/v1", tags=["notifications"])


@router.get("/notifications")
def get_notifications(
    current_user: User = Depends(get_current_user),
    status: str = Query("unread", pattern="^(unread|read|all)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    items = active_notifications_query(db).order_by(Notification.id.desc()).all()

    if status != "all":
        items = [
            n
            for n in items
            if status_for_user(db, n, current_user.login) == status
        ]

    total = len(items)
    page = items[offset : offset + limit]
    unread_count = unread_count_for_user(db, current_user.login)

    return {
        "success": True,
        "total": total,
        "unread_count": unread_count,
        "limit": limit,
        "offset": offset,
        "data": [
            {
                "id": n.id,
                "accident_id": n.accident_id,
                "status": status_for_user(db, n, current_user.login),
                "accident_status": n.accident.event_status if n.accident else None,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in page
        ],
    }


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read_endpoint(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not mark_notification_read(db, notification_id, current_user.login):
        raise HTTPException(status_code=404, detail="Уведомление не найдено")

    db.commit()
    await push_unread_count_ws(db, manager, current_user.login)

    return {
        "success": True,
        "notification_id": notification_id,
        "status": "read",
    }


@router.put("/notifications/read-all")
async def mark_all_notifications_read_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    mark_all_notifications_read(db, current_user.login)
    db.commit()
    await push_unread_count_ws(db, manager, current_user.login)

    return {"success": True}
