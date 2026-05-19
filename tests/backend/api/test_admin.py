# тесты /api/v1/admin (только is_admin)
import hashlib
from datetime import timedelta

import pytest

from src.traffic_dtp.db.models.user import User
from src.traffic_dtp.db.models.user_session import UserSession
from src.traffic_dtp.services import user_session as session_service
from src.traffic_dtp.services.auth import hash_password


@pytest.fixture
def admin_user(db_session):
    login = "admin_test"
    password = "admin_pw_99"
    db_session.merge(
        User(
            login=login,
            password_hash=hashlib.sha256(password.encode()).hexdigest(),
            is_admin=True,
        )
    )
    db_session.commit()
    return {"login": login, "password": password}


@pytest.fixture
def admin_headers(client, admin_user):
    r = client.post(
        "/api/v1/auth/login",
        json={"login": admin_user["login"], "password": admin_user["password"]},
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_non_admin_cannot_create_user(client, sample_user):
    r_login = client.post(
        "/api/v1/auth/login",
        json={"login": sample_user["login"], "password": sample_user["password"]},
    )
    headers = {"Authorization": f"Bearer {r_login.json()['token']}"}
    r = client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={"login": "new_u", "password": "password1", "is_admin": False},
    )
    assert r.status_code == 403


def test_password_stored_as_hash_not_plaintext(client, admin_headers, db_session):
    plain = "PlainSecret99!"
    login = "hash_only_user"
    r = client.post(
        "/api/v1/admin/users",
        headers=admin_headers,
        json={"login": login, "password": plain, "is_admin": False},
    )
    assert r.status_code == 200, r.text
    assert "password" not in r.json()
    assert "password_hash" not in r.json()

    user = db_session.query(User).filter(User.login == login).one()
    assert user.password_hash != plain
    assert user.password_hash == hash_password(plain)
    assert len(user.password_hash) == 64


def test_admin_list_users_never_exposes_password_hash(client, admin_headers):
    r = client.get("/api/v1/admin/users", headers=admin_headers)
    assert r.status_code == 200
    for row in r.json()["data"]:
        assert "password" not in row
        assert "password_hash" not in row


def test_admin_creates_user(client, admin_headers):
    r = client.post(
        "/api/v1/admin/users",
        headers=admin_headers,
        json={"login": "created_by_admin", "password": "password1", "is_admin": False},
    )
    assert r.status_code == 200, r.text
    assert r.json()["login"] == "created_by_admin"

    r_login = client.post(
        "/api/v1/auth/login",
        json={"login": "created_by_admin", "password": "password1"},
    )
    assert r_login.status_code == 200


def test_admin_lists_users(client, admin_headers):
    r = client.get("/api/v1/admin/users", headers=admin_headers)
    assert r.status_code == 200
    assert any(u["login"] == "admin_test" for u in r.json()["data"])


def test_admin_lists_sessions_last_24h(client, admin_headers, db_session):
    audit_login = "session_audit_user"
    now = session_service.utc_now()
    db_session.add(
        UserSession(
            user_login=audit_login,
            token_hash="a" * 64,
            ip_address="192.168.1.10",
            user_agent="Swagger-Test/1.0",
            login_at=now - timedelta(hours=2),
            logout_at=now - timedelta(hours=1),
            status=session_service.STATUS_CLOSED,
        )
    )
    db_session.add(
        UserSession(
            user_login=audit_login,
            token_hash="b" * 64,
            ip_address="10.0.0.5",
            user_agent="OldBrowser/0.1",
            login_at=now - timedelta(hours=48),
            logout_at=now - timedelta(hours=47),
            status=session_service.STATUS_CLOSED,
        )
    )
    db_session.commit()

    r = client.get("/api/v1/admin/sessions?hours=24", headers=admin_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["success"] is True
    assert body["period_hours"] == 24

    audit_rows = [row for row in body["data"] if row["user_login"] == audit_login]
    assert len(audit_rows) == 1
    row = audit_rows[0]
    assert row["ip_address"] == "192.168.1.10"
    assert "Swagger-Test" in row["user_agent"]
    assert row["duration_seconds"] == 3600
    assert "token_hash" not in row
    assert not any("OldBrowser" in r["user_agent"] for r in body["data"])


def test_non_admin_cannot_list_sessions(client, sample_user):
    r_login = client.post(
        "/api/v1/auth/login",
        json={"login": sample_user["login"], "password": sample_user["password"]},
    )
    headers = {"Authorization": f"Bearer {r_login.json()['token']}"}
    r = client.get("/api/v1/admin/sessions", headers=headers)
    assert r.status_code == 403
