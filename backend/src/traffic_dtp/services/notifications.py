from sqlalchemy.orm import Session
from src.traffic_dtp.db.models import Notification, Accident, User


def create_notification(db: Session, accident_id: int) -> list[Notification]:
    accident = db.query(Accident).filter(
        Accident.id == accident_id,
        Accident.is_active == True
    ).first()

    if not accident:
        return []

    users = db.query(User).all()
    notifications = []

    for user in users:
        db.query(Notification).filter(
            Notification.accident_id == accident_id,
            Notification.user_login == user.login,
            Notification.status == "unread"
        ).delete()

        notification = Notification(
            accident_id=accident_id,
            user_login=user.login,
            status="unread",
            is_sent=True,
        )
        db.add(notification)
        notifications.append(notification)

    db.flush()
    return notifications