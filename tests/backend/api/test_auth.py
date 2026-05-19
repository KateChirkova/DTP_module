# тесты auth: login, verify, logout, сессии
import hashlib
from datetime import datetime, timedelta, timezone

import pytest

from src.traffic_dtp.db.models.user import User
from src.traffic_dtp.db.models.user_session import UserSession
from src.traffic_dtp.services import user_session as session_service


def test_login_response_never_returns_password(client, sample_user):
    r = client.post(
        "/api/v1/auth/login",
        json={"login": sample_user["login"], "password": sample_user["password"]},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "password" not in body
    assert "password_hash" not in body


def test_login_wrong_password(client, db_session):
    db_session.merge(
        User(
            login="auth_flow_u1",
            password_hash=hashlib.sha256(b"right").hexdigest(),
        )
    )
    db_session.commit()

    r = client.post(
        "/api/v1/auth/login",
        json={"login": "auth_flow_u1", "password": "wrong"},
    )
    assert r.status_code == 401


def test_login_unknown_user(client):
    r = client.post(
        "/api/v1/auth/login",
        json={"login": "no_such_user_x", "password": "x"},
    )
    assert r.status_code == 401


def test_login_missing_fields_422(client):
    r = client.post("/api/v1/auth/login", json={})
    assert r.status_code == 422


def test_verify_without_bearer_unauthorized(client):
    r = client.get("/api/v1/auth/verify")
    assert r.status_code == 401


def test_verify_invalid_token(client):
    r = client.get(
        "/api/v1/auth/verify",
        headers={"Authorization": "Bearer jwt-not-a-real-session"},
    )
    assert r.status_code == 401


def test_login_populates_all_session_fields(client, db_session, sample_user):
    login = sample_user["login"]
    password = sample_user["password"]

    r = client.post(
        "/api/v1/auth/login",
        json={"login": login, "password": password},
        headers={
            "User-Agent": "DTP-TestBrowser/1.0",
            "X-Forwarded-For": "203.0.113.50",
        },
    )
    assert r.status_code == 200, r.text
    token = r.json()["token"]
    assert token.startswith(session_service.TOKEN_PREFIX)

    session = (
        db_session.query(UserSession)
        .filter(UserSession.user_login == login, UserSession.status == session_service.STATUS_ACTIVE)
        .first()
    )
    assert session is not None
    assert session.id is not None
    assert session.user_login == login
    assert session.token_hash == session_service.hash_token(token)
    assert len(session.token_hash) == 64
    assert session.ip_address == "203.0.113.50"
    assert "DTP-TestBrowser" in session.user_agent
    assert session.login_at is not None
    assert session.logout_at is None
    assert session.status == session_service.STATUS_ACTIVE


def test_relogin_closes_previous_session(client, db_session, sample_user):
    login = sample_user["login"]
    password = sample_user["password"]
    body = {"login": login, "password": password}

    r1 = client.post("/api/v1/auth/login", json=body)
    assert r1.status_code == 200
    first_id = (
        db_session.query(UserSession)
        .filter(UserSession.user_login == login)
        .order_by(UserSession.id.asc())
        .first()
        .id
    )

    r2 = client.post("/api/v1/auth/login", json=body)
    assert r2.status_code == 200

    first = db_session.get(UserSession, first_id)
    second = (
        db_session.query(UserSession)
        .filter(UserSession.user_login == login, UserSession.status == session_service.STATUS_ACTIVE)
        .first()
    )
    assert first.status == session_service.STATUS_CLOSED
    assert first.logout_at is not None
    assert second is not None
    assert second.id != first_id
    assert second.status == session_service.STATUS_ACTIVE
    assert second.logout_at is None


def test_logout_fills_logout_at_and_status(client, db_session, sample_user):
    login = sample_user["login"]
    password = sample_user["password"]

    r_login = client.post(
        "/api/v1/auth/login",
        json={"login": login, "password": password},
    )
    token = r_login.json()["token"]
    session = (
        db_session.query(UserSession)
        .filter(UserSession.user_login == login, UserSession.status == session_service.STATUS_ACTIVE)
        .one()
    )

    r_out = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_out.status_code == 200

    db_session.refresh(session)
    assert session.status == session_service.STATUS_CLOSED
    assert session.logout_at is not None


def test_login_verify_logout_verify_fails(client, sample_user):
    login = sample_user["login"]
    password = sample_user["password"]

    r_login = client.post(
        "/api/v1/auth/login",
        json={"login": login, "password": password},
    )
    assert r_login.status_code == 200
    token = r_login.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    r_verify = client.get("/api/v1/auth/verify", headers=headers)
    assert r_verify.status_code == 200
    assert r_verify.json()["login"] == login

    r_out = client.post("/api/v1/auth/logout", headers=headers)
    assert r_out.status_code == 200

    r_after = client.get("/api/v1/auth/verify", headers=headers)
    assert r_after.status_code == 401


@pytest.fixture
def auth_user(db_session):
    login = "session_expiry_user"
    password = "secret123"
    db_session.merge(
        User(
            login=login,
            password_hash=hashlib.sha256(password.encode()).hexdigest(),
        )
    )
    db_session.commit()
    return login, password


def test_verify_ok_within_24h(client, auth_user):
    login, password = auth_user
    r = client.post(
        "/api/v1/auth/login",
        json={"login": login, "password": password},
    )
    assert r.status_code == 200, r.text
    token = r.json()["token"]

    res = client.get(
        "/api/v1/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json().get("login") == login


def test_verify_fails_after_24h_from_login_at(client, db_session, auth_user):
    login, password = auth_user
    r = client.post(
        "/api/v1/auth/login",
        json={"login": login, "password": password},
    )
    assert r.status_code == 200, r.text
    token = r.json()["token"]

    session = db_session.query(UserSession).filter(UserSession.user_login == login).first()
    assert session is not None
    past = datetime.now(timezone.utc) - timedelta(hours=25)
    session.login_at = past
    db_session.commit()

    res = client.get(
        "/api/v1/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 401

    db_session.refresh(session)
    assert session.status == session_service.STATUS_EXPIRED
    assert session.logout_at is not None
