from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.traffic_dtp.api.deps import get_current_user
from src.traffic_dtp.db.session import get_db
from src.traffic_dtp.db.models import Notification, Accident, User
from src.traffic_dtp.api.routers.ws import manager

router = APIRouter(prefix="/api/v1", tags=["notifications"])


@router.get("/notifications")
async def get_notifications(
        current_user: User = Depends(get_current_user),
        status: str = Query("unread", pattern="^(unread|read|all)$"),
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
):
    query = (
        db.query(Notification)
        .join(Accident, Notification.accident_id == Accident.id)
        .filter(Notification.user_login == current_user.login)
        .filter(Accident.is_active == True)
    )

    if status != "all":
        query = query.filter(Notification.status == status)

    total = query.count()
    notifications = query.order_by(Notification.id.desc()).offset(offset).limit(limit).all()

    unread_count = (
        db.query(Notification)
        .join(Accident)
        .filter(Notification.user_login == current_user.login)
        .filter(Notification.status == "unread")
        .filter(Accident.is_active == True)
        .count()
    )

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
                "status": n.status,
                "accident_status": n.accident.event_status if n.accident else None,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "is_sent": n.is_sent,
            }
            for n in notifications
        ],
    }


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
        notification_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    notification = (
        db.query(Notification)
        .join(Accident, Notification.accident_id == Accident.id)
        .filter(Notification.id == notification_id)
        .filter(Notification.user_login == current_user.login)
        .filter(Accident.is_active == True)
        .first()
    )

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.status = "read"
    notification.is_sent = True
    db.commit()

    unread_count = (
        db.query(Notification)
        .join(Accident)
        .filter(Notification.user_login == current_user.login)
        .filter(Notification.status == "unread")
        .filter(Accident.is_active == True)
        .count()
    )

    await manager.send_to_user(current_user.login, {
        "event": "notifications_updated",
        "data": {"unread_count": unread_count}
    })

    return {
        "success": True,
        "notification_id": notification.id,
        "status": notification.status,
    }


@router.put("/notifications/read-all")
async def mark_all_notifications_read(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db.query(Notification).filter(
        Notification.user_login == current_user.login,
        Notification.status == "unread"
    ).update(
        {"status": "read", "is_sent": True},
        synchronize_session=False
    )
    db.commit()

    await manager.send_to_user(current_user.login, {
        "event": "notifications_updated",
        "data": {"unread_count": 0}
    })

    return {
        "success": True
    }