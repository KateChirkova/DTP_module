from sqlalchemy.orm import Session
from src.traffic_dtp.db.models import Notification, Accident

def create_notification(db: Session, accident_id: int, event_type: str = "new") -> Notification:
    accident = db.query(Accident).filter(Accident.id == accident_id, Accident.is_active == True).first()
    if not accident:
        print(f"No active accident {accident_id}")
        return None

    db.query(Notification).filter(Notification.accident_id == accident_id, Notification.status == "unread").delete()

    notification = Notification(
        accident_id=accident_id,
        status="unread",
        is_sent=True,
    )
    db.add(notification)
    db.flush()
    print(f"Notification created for accident {accident_id}")
    return notification