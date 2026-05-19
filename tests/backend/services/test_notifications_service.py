# тесты сервиса notifications (общая модель + reads)
import hashlib

from src.traffic_dtp.db.models import Accident, Notification, NotificationRead, User
from src.traffic_dtp.services.notifications import (
    create_notification,
    delete_notifications_for_accident,
    is_read_for_user,
    mark_notification_read,
    unread_counts_by_user,
)


def test_create_notification_single_row(db_session):
    db_session.merge(User(login="u_a", password_hash=hashlib.sha256(b"p").hexdigest()))
    db_session.merge(User(login="u_b", password_hash=hashlib.sha256(b"p").hexdigest()))

    acc = Accident(
        bbox_x1=0,
        bbox_y1=0,
        bbox_x2=10,
        bbox_y2=10,
        confidence=0.9,
        event_status="new",
        is_active=True,
        missed_screenshots=0,
    )
    db_session.add(acc)
    db_session.commit()

    created = create_notification(db_session, acc.id)
    assert created is not None
    db_session.commit()

    assert db_session.query(Notification).filter(Notification.accident_id == acc.id).count() == 1
    assert is_read_for_user(db_session, created.id, "u_a") is False
    assert is_read_for_user(db_session, created.id, "u_b") is False


def test_create_notification_idempotent(db_session):
    db_session.merge(User(login="solo", password_hash=hashlib.sha256(b"p").hexdigest()))
    acc = Accident(
        bbox_x1=0,
        bbox_y1=0,
        bbox_x2=5,
        bbox_y2=5,
        confidence=0.8,
        event_status="new",
        is_active=True,
        missed_screenshots=0,
    )
    db_session.add(acc)
    db_session.commit()

    first = create_notification(db_session, acc.id)
    second = create_notification(db_session, acc.id)
    db_session.commit()

    assert first is not None and second is not None
    assert first.id == second.id
    assert db_session.query(Notification).count() == 1


def test_mark_read_only_for_one_user(db_session):
    db_session.merge(User(login="u_a", password_hash=hashlib.sha256(b"p").hexdigest()))
    db_session.merge(User(login="u_b", password_hash=hashlib.sha256(b"p").hexdigest()))
    acc = Accident(
        bbox_x1=0,
        bbox_y1=0,
        bbox_x2=5,
        bbox_y2=5,
        confidence=0.8,
        event_status="new",
        is_active=True,
        missed_screenshots=0,
    )
    db_session.add(acc)
    db_session.commit()

    n = create_notification(db_session, acc.id)
    assert mark_notification_read(db_session, n.id, "u_a")
    db_session.commit()

    assert is_read_for_user(db_session, n.id, "u_a") is True
    assert is_read_for_user(db_session, n.id, "u_b") is False


def test_delete_notifications_for_accident(db_session):
    db_session.merge(User(login="solo", password_hash=hashlib.sha256(b"p").hexdigest()))
    acc = Accident(
        bbox_x1=0,
        bbox_y1=0,
        bbox_x2=5,
        bbox_y2=5,
        confidence=0.8,
        event_status="new",
        is_active=True,
        missed_screenshots=0,
    )
    db_session.add(acc)
    db_session.flush()
    n = Notification(accident_id=acc.id)
    db_session.add(n)
    db_session.flush()
    db_session.add(NotificationRead(notification_id=n.id, user_login="solo"))
    db_session.commit()

    deleted = delete_notifications_for_accident(db_session, acc.id)
    assert deleted >= 1
    db_session.commit()

    assert db_session.query(Notification).filter(Notification.accident_id == acc.id).count() == 0
    assert db_session.query(NotificationRead).count() == 0


def test_create_notification_returns_none_if_accident_missing(db_session):
    assert create_notification(db_session, 99999) is None


def test_unread_counts_by_user_grouped(db_session):
    db_session.merge(User(login="u_a", password_hash=hashlib.sha256(b"p").hexdigest()))
    db_session.merge(User(login="u_b", password_hash=hashlib.sha256(b"p").hexdigest()))
    acc = Accident(
        bbox_x1=0,
        bbox_y1=0,
        bbox_x2=10,
        bbox_y2=10,
        confidence=0.9,
        event_status="new",
        is_active=True,
        missed_screenshots=0,
    )
    db_session.add(acc)
    db_session.commit()

    n = create_notification(db_session, acc.id)
    assert n is not None
    mark_notification_read(db_session, n.id, "u_a")
    db_session.commit()

    counts = unread_counts_by_user(db_session)
    assert counts["u_a"] == 0
    assert counts["u_b"] == 1
