from __future__ import annotations

import logging

from sqlalchemy import and_, exists, func, true

logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session

from src.traffic_dtp.db.models import Accident, Notification, NotificationRead, User


# только уведомления по активным ДТП
def active_notifications_query(db: Session):
    return (
        db.query(Notification)
        .join(Accident, Notification.accident_id == Accident.id)
        .filter(Accident.is_active.is_(True))
    )


def _read_exists(db: Session, notification_id: int, user_login: str):
    return exists().where(
        NotificationRead.notification_id == notification_id,
        NotificationRead.user_login == user_login,
    )


def is_read_for_user(db: Session, notification_id: int, user_login: str) -> bool:
    return (
        db.query(NotificationRead.id)
        .filter(
            NotificationRead.notification_id == notification_id,
            NotificationRead.user_login == user_login,
        )
        .first()
        is not None
    )


def status_for_user(db: Session, notification: Notification, user_login: str) -> str:
    return "read" if is_read_for_user(db, notification.id, user_login) else "unread"


def delete_notifications_for_accident(db: Session, accident_id: int) -> int:
    notifications = (
        db.query(Notification).filter(Notification.accident_id == accident_id).all()
    )
    for notification in notifications:
        db.delete(notification)
    if notifications:
        db.flush()
    return len(notifications)


def create_notification(db: Session, accident_id: int) -> Notification | None:
    accident = (
        db.query(Accident)
        .filter(Accident.id == accident_id, Accident.is_active.is_(True))
        .first()
    )
    if not accident:
        logger.error(
            "create_notification: active accident not found accident_id=%s",
            accident_id,
        )
        return None

    existing = (
        db.query(Notification).filter(Notification.accident_id == accident_id).first()
    )
    if existing:
        return existing

    notification = Notification(accident_id=accident_id)
    db.add(notification)
    db.flush()
    return notification


def mark_notification_read(db: Session, notification_id: int, user_login: str) -> bool:
    notification = (
        active_notifications_query(db)
        .filter(Notification.id == notification_id)
        .first()
    )
    if not notification:
        logger.warning(
            "mark_notification_read: notification not found or inactive "
            "notification_id=%s user=%s",
            notification_id,
            user_login,
        )
        return False

    if is_read_for_user(db, notification_id, user_login):
        return True

    db.add(
        NotificationRead(
            notification_id=notification_id,
            user_login=user_login,
        )
    )
    db.flush()
    return True


def mark_all_notifications_read(db: Session, user_login: str) -> int:
    unread = (
        active_notifications_query(db)
        .filter(~_read_exists(db, Notification.id, user_login))
        .all()
    )
    for notification in unread:
        db.add(
            NotificationRead(
                notification_id=notification.id,
                user_login=user_login,
            )
        )
    if unread:
        db.flush()
    return len(unread)


def unread_count_for_user(db: Session, user_login: str) -> int:
    return (
        active_notifications_query(db)
        .filter(~_read_exists(db, Notification.id, user_login))
        .count()
    )


# один запрос: непрочитанные по всем пользователям
def unread_counts_by_user(db: Session) -> dict[str, int]:
    all_logins = [row[0] for row in db.query(User.login).all()]
    counts = dict.fromkeys(all_logins, 0)
    if not all_logins:
        return counts

    rows = (
        db.query(User.login, func.count(Notification.id))
        .select_from(User)
        .join(Notification, true())
        .join(Accident, Accident.id == Notification.accident_id)
        .outerjoin(
            NotificationRead,
            and_(
                NotificationRead.notification_id == Notification.id,
                NotificationRead.user_login == User.login,
            ),
        )
        .filter(Accident.is_active.is_(True))
        .filter(NotificationRead.id.is_(None))
        .group_by(User.login)
        .all()
    )
    for login, count in rows:
        counts[login] = count
    return counts


async def push_unread_count_ws(db, manager, user_login: str) -> None:
    count = unread_count_for_user(db, user_login)
    await manager.send_to_user(
        user_login,
        {"event": "notifications_updated", "data": {"unread_count": count}},
    )


async def push_unread_counts_all_users(db, manager) -> None:
    for user_login, count in unread_counts_by_user(db).items():
        await manager.send_to_user(
            user_login,
            {"event": "notifications_updated", "data": {"unread_count": count}},
        )
