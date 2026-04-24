from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.traffic_dtp.db.session import get_db
from src.traffic_dtp.db.models import Notification, Accident

router = APIRouter(prefix="/api", tags=["notifications"])


@router.get("/v1/notifications")
def get_notifications(
    status: str = Query("unread", pattern="^(unread|read|all)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Notification)
        .join(Accident, Notification.accident_id == Accident.id)
        .filter(Accident.is_active == True)
    )

    if status != "all":
        query = query.filter(Notification.status == status)

    total = query.count()
    notifications = query.order_by(Notification.id.desc()).offset(offset).limit(limit).all()

    unread_count = (
        db.query(Notification)
        .join(Accident, Notification.accident_id == Accident.id)
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
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "is_sent": n.is_sent,
            }
            for n in notifications
        ],
    }


@router.put("/v1/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db)):
    notification = (
        db.query(Notification)
        .join(Accident, Notification.accident_id == Accident.id)
        .filter(Notification.id == notification_id)
        .filter(Accident.is_active == True)
        .first()
    )

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found or accident resolved")

    notification.status = "read"
    notification.is_sent = True
    db.commit()

    return {
        "success": True,
        "notification_id": notification.id,
        "status": notification.status,
    }