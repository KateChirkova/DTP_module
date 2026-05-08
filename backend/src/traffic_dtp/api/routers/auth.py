from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from pydantic import BaseModel
from src.traffic_dtp.db.session import get_db
from src.traffic_dtp.db.models.user import User
from src.traffic_dtp.db.models.user_session import UserSession
from src.traffic_dtp.api.deps import get_current_user
import uuid, hashlib

security = HTTPBearer()
router = APIRouter(prefix="/api/v1", tags=["auth"])


class LoginRequest(BaseModel):
    login: str
    password: str


@router.post("/auth/login")
def login(request: Request, req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login == req.login).first()
    if not user or user.password_hash != hashlib.sha256(req.password.encode()).hexdigest():
        raise HTTPException(401, "Неверный логин/пароль")

    db.query(UserSession).filter(
        UserSession.user_login == user.login, UserSession.status == "active"
    ).update({"status": "closed", "logout_at": func.now()})

    token = f"jwt-{uuid.uuid4().hex[:16]}"
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    new_session = UserSession(
        user_login=user.login,
        token_hash=token_hash,
        ip_address=request.client.host,
        user_agent=str(request.headers.get("user-agent", "web")),
        login_at=func.now(),
        status="active"
    )
    db.add(new_session)
    db.commit()

    return {
        "success": True,
        "token": token,
        "expires_in": 60,
        "user": user.login
    }


@router.get("/auth/verify")
def verify_token(current_user: User = Depends(get_current_user)): 
    return {
        "success": True,
        "login": current_user.login,
        "expires_in": 60
    }


@router.post("/auth/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    token = Depends(security).authorization
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    session = db.query(UserSession).filter(
        UserSession.token_hash == token_hash, UserSession.status == "active"
    ).first()

    if session:
        session.status = "closed"
        session.logout_at = func.now()
        db.commit()
        print(f"Created session: {new_session.id}, hash={token_hash[:16]}..., token={token[:16]}...")
    return {"success": True, "message": "Логаут"}