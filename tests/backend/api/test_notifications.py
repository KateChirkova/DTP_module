# тесты REST /api/v1/notifications
from datetime import datetime, timezone

import pytest

from src.traffic_dtp.db.models import Accident, Notification, NotificationRead, User
from src.traffic_dtp.services.auth import hash_password


def _add_accident(db_session, *, confidence: float = 0.9) -> Accident:
    now = datetime.now(timezone.utc)
    acc = Accident(
        bbox_x1=1,
        bbox_y1=2,
        bbox_x2=10,
        bbox_y2=20,
        confidence=confidence,
        first_seen=now,
        last_seen=now,
        event_status="new",
        is_active=True,
        missed_screenshots=0,
    )
    db_session.add(acc)
    db_session.flush()
    return acc


def _add_notification(db_session, accident: Accident, *, read_for: str | None = None) -> Notification:
    n = Notification(accident_id=accident.id)
    db_session.add(n)
    db_session.flush()
    if read_for:
        db_session.add(NotificationRead(notification_id=n.id, user_login=read_for))
    return n


def test_get_notifications_empty(client, auth_headers):
    r = client.get("/api/v1/notifications", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["total"] == 0
    assert data["unread_count"] == 0
    assert data["data"] == []


def test_get_notifications_requires_auth(client):
    r = client.get("/api/v1/notifications")
    assert r.status_code == 401


def test_mark_notification_read(client, db_session, sample_user, auth_headers):
    acc = _add_accident(db_session)
    n = _add_notification(db_session, acc)
    db_session.commit()

    r = client.put(f"/api/v1/notifications/{n.id}/read", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["status"] == "read"

    r2 = client.get("/api/v1/notifications?status=unread", headers=auth_headers)
    assert r2.json()["unread_count"] == 0


def test_mark_notification_read_not_found(client, auth_headers):
    r = client.put("/api/v1/notifications/99999/read", headers=auth_headers)
    assert r.status_code == 404


def test_mark_read_independent_per_user(client, db_session, sample_user, auth_headers):
    other_login = "other_user_notify"
    other_password = "other_pw_88"
    db_session.merge(
        User(
            login=other_login,
            password_hash=hash_password(other_password),
        )
    )
    acc = _add_accident(db_session)
    n = _add_notification(db_session, acc)
    db_session.commit()

    r_other = client.post(
        "/api/v1/auth/login",
        json={"login": other_login, "password": other_password},
    )
    assert r_other.status_code == 200
    other_headers = {"Authorization": f"Bearer {r_other.json()['token']}"}

    r = client.put(f"/api/v1/notifications/{n.id}/read", headers=other_headers)
    assert r.status_code == 200

    r_sample = client.get("/api/v1/notifications?status=unread", headers=auth_headers)
    assert r_sample.json()["unread_count"] == 1

    r_other_list = client.get("/api/v1/notifications?status=unread", headers=other_headers)
    assert r_other_list.json()["unread_count"] == 0


def test_mark_all_notifications_read(client, db_session, sample_user, auth_headers):
    acc = _add_accident(db_session)
    _add_notification(db_session, acc)
    db_session.commit()

    r = client.put("/api/v1/notifications/read-all", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True

    r2 = client.get("/api/v1/notifications?status=unread", headers=auth_headers)
    assert r2.json()["unread_count"] == 0


def test_notifications_status_filter_all(client, db_session, sample_user, auth_headers):
    acc = _add_accident(db_session)
    _add_notification(db_session, acc, read_for=sample_user["login"])
    db_session.commit()

    r_unread = client.get("/api/v1/notifications?status=unread", headers=auth_headers)
    assert r_unread.json()["total"] == 0

    r_all = client.get("/api/v1/notifications?status=all", headers=auth_headers)
    assert r_all.json()["total"] == 1


@pytest.mark.parametrize(
    "query",
    [
        "status=invalid",
        "limit=0",
        "limit=101",
        "offset=-1",
    ],
)
def test_notifications_query_validation_422(client, auth_headers, query):
    r = client.get(f"/api/v1/notifications?{query}", headers=auth_headers)
    assert r.status_code == 422


def test_notifications_pagination_offset(client, db_session, sample_user, auth_headers):
    for i in range(3):
        acc = _add_accident(db_session, confidence=0.7 + i * 0.01)
        _add_notification(db_session, acc)
    db_session.commit()

    r = client.get(
        "/api/v1/notifications?status=all&limit=1&offset=1",
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["limit"] == 1
    assert data["offset"] == 1
    assert data["total"] == 3
    assert len(data["data"]) == 1
