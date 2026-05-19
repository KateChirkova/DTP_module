from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.traffic_dtp.api.deps import get_current_admin
from src.traffic_dtp.db.models.user import User
from src.traffic_dtp.db.session import get_db
from src.traffic_dtp.services import user_session as session_service
from src.traffic_dtp.services.auth import hash_password

# только is_admin=true
router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)],
)


class CreateUserBody(BaseModel):
    login: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    is_admin: bool = False


@router.post("/users")
def create_user(body: CreateUserBody, db: Session = Depends(get_db)):
    login = body.login.strip()
    if not login:
        raise HTTPException(status_code=400, detail="Логин не может быть пустым")
    if db.query(User).filter(User.login == login).first():
        raise HTTPException(status_code=409, detail=f"Пользователь «{login}» уже существует")

    db.add(
        User(
            login=login,
            password_hash=hash_password(body.password),
            is_admin=body.is_admin,
        )
    )
    db.commit()
    return {"success": True, "login": login, "is_admin": body.is_admin}


@router.get("/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.login).all()
    return {
        "success": True,
        "data": [
            {"login": u.login, "is_admin": bool(u.is_admin), "created_at": u.created_at}
            for u in users
        ],
    }


@router.get("/sessions", summary="Сессии за период")
def list_sessions(
    hours: int = Query(24, ge=1, le=168, description="Сессии за последние N часов"),
    db: Session = Depends(get_db),
):
    now = session_service.utc_now()
    since = now - timedelta(hours=hours)
    sessions = session_service.list_sessions_since(db, since)

    rows = [session_service.session_to_dict(s) for s in sessions]
    active = sum(1 for r in rows if r["status"] == session_service.STATUS_ACTIVE)
    closed = sum(1 for r in rows if r["status"] == session_service.STATUS_CLOSED)
    expired = sum(1 for r in rows if r["status"] == session_service.STATUS_EXPIRED)
    unique_users = len({r["user_login"] for r in rows})

    return {
        "success": True,
        "period_hours": hours,
        "since": since,
        "until": now,
        "summary": {
            "total": len(rows),
            "active": active,
            "closed": closed,
            "expired": expired,
            "unique_users": unique_users,
        },
        "data": rows,
    }
