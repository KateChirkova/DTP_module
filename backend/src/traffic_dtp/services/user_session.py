# создание, проверка и закрытие user_sessions
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Request
from sqlalchemy.orm import Session

from src.traffic_dtp.db.models.user_session import UserSession

SESSION_TTL_HOURS = 24
TOKEN_PREFIX = "jwt-"

STATUS_ACTIVE = "active"
STATUS_CLOSED = "closed"
STATUS_EXPIRED = "expired"

USER_AGENT_MAX_LEN = 512


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def generate_token() -> str:
    return f"{TOKEN_PREFIX}{uuid.uuid4().hex[:16]}"


def resolve_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
        if ip:
            return ip[:45]
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()[:45]
    if request.client and request.client.host:
        return request.client.host[:45]
    return "unknown"


def resolve_user_agent(request: Request) -> str:
    ua = request.headers.get("user-agent")
    if ua and ua.strip():
        return ua.strip()[:USER_AGENT_MAX_LEN]
    return "unknown"


def _login_at_utc(session: UserSession) -> datetime | None:
    if session.login_at is None:
        return None
    login_at = session.login_at
    if login_at.tzinfo is None:
        return login_at.replace(tzinfo=timezone.utc)
    return login_at.astimezone(timezone.utc)


def session_remaining_seconds(session: UserSession, *, now: datetime | None = None) -> int:
    login_at = _login_at_utc(session)
    if login_at is None:
        return 0
    now = now or utc_now()
    ttl = SESSION_TTL_HOURS * 3600
    return max(0, int(ttl - (now - login_at).total_seconds()))


def is_session_expired(session: UserSession, *, now: datetime | None = None) -> bool:
    login_at = _login_at_utc(session)
    if login_at is None:
        return True
    now = now or utc_now()
    return (now - login_at) > timedelta(hours=SESSION_TTL_HOURS)


# повторный вход — закрыть старые active-сессии
def close_active_sessions_for_user(db: Session, user_login: str) -> int:
    now = utc_now()
    count = (
        db.query(UserSession)
        .filter(
            UserSession.user_login == user_login,
            UserSession.status == STATUS_ACTIVE,
        )
        .update(
            {"status": STATUS_CLOSED, "logout_at": now},
            synchronize_session=False,
        )
    )
    if count:
        db.commit()
    return count


def create_session(db: Session, user_login: str, request: Request) -> tuple[str, UserSession]:
    raw_token = generate_token()
    now = utc_now()
    session = UserSession(
        user_login=user_login,
        token_hash=hash_token(raw_token),
        ip_address=resolve_client_ip(request),
        user_agent=resolve_user_agent(request),
        login_at=now,
        logout_at=None,
        status=STATUS_ACTIVE,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return raw_token, session


def find_active_session_by_token(db: Session, raw_token: str) -> UserSession | None:
    token_hash = hash_token(raw_token)
    return (
        db.query(UserSession)
        .filter(
            UserSession.token_hash == token_hash,
            UserSession.status == STATUS_ACTIVE,
        )
        .first()
    )


def _set_session_status(db: Session, session: UserSession, status: str) -> None:
    session.status = status
    session.logout_at = utc_now()
    db.commit()


def close_session(db: Session, session: UserSession) -> None:
    _set_session_status(db, session, STATUS_CLOSED)


def expire_session(db: Session, session: UserSession) -> None:
    _set_session_status(db, session, STATUS_EXPIRED)


def session_duration_seconds(session: UserSession, *, now: datetime | None = None) -> int | None:
    login_at = _login_at_utc(session)
    if login_at is None:
        return None

    if session.logout_at is not None:
        end = session.logout_at
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        else:
            end = end.astimezone(timezone.utc)
    elif session.status == STATUS_ACTIVE:
        end = now or utc_now()
    else:
        return None

    return max(0, int((end - login_at).total_seconds()))


def list_sessions_since(db: Session, since: datetime) -> list[UserSession]:
    return (
        db.query(UserSession)
        .filter(UserSession.login_at >= since)
        .order_by(UserSession.login_at.desc())
        .all()
    )


def session_to_dict(session: UserSession) -> dict:
    return {
        "id": session.id,
        "user_login": session.user_login,
        "ip_address": session.ip_address,
        "user_agent": session.user_agent,
        "login_at": _login_at_utc(session),
        "logout_at": session.logout_at,
        "status": session.status,
        "duration_seconds": session_duration_seconds(session),
        "is_active": session.status == STATUS_ACTIVE,
    }
