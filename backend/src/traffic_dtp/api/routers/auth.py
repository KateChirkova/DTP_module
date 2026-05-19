from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.traffic_dtp.api.deps import get_current_user, security
from src.traffic_dtp.db.models.user import User
from src.traffic_dtp.db.session import get_db
from src.traffic_dtp.services import user_session as session_service
from src.traffic_dtp.services.auth import verify_password

router = APIRouter(prefix="/api/v1", tags=["auth"])


class LoginRequest(BaseModel):
    login: str
    password: str


# один active-токен на пользователя; старые сессии закрываются
@router.post("/auth/login")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login == body.login).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    session_service.close_active_sessions_for_user(db, user.login)
    raw_token, session = session_service.create_session(db, user.login, request)

    return {
        "success": True,
        "token": raw_token,
        "expires_in": session_service.session_remaining_seconds(session),
        "user": user.login,
    }


@router.get("/auth/verify")
def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = session_service.find_active_session_by_token(db, credentials.credentials)
    expires_in = session_service.session_remaining_seconds(session) if session else 0
    return {
        "success": True,
        "login": current_user.login,
        "expires_in": expires_in,
    }


@router.post("/auth/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session_service.close_active_sessions_for_user(db, current_user.login)
    return {"success": True, "message": "Выход выполнен"}
