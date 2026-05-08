from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.traffic_dtp.db.session import get_db
from src.traffic_dtp.db.models.user import User
from src.traffic_dtp.db.models.user_session import UserSession
import hashlib
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta

security = HTTPBearer()

def get_current_user(authorization: str = Depends(security), db: Session = Depends(get_db)):
    raw_token = authorization.credentials
    print(f"RAW TOKEN: {raw_token}")

    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    print(f"TOKEN HASH: {token_hash[:16]}...")

    session = db.query(UserSession).filter(
        and_(
            UserSession.token_hash == token_hash,
            UserSession.status == "active"
        )
    ).first()

    print(f"Sessions in DB: {db.query(UserSession).filter(UserSession.status == 'active').count()}")
    print(f"get_current_user: {authorization.credentials[:20]}...")

    if not session:
        print(f"Session NOT FOUND: {token_hash[:16]}...")
        raise HTTPException(401, "Сессия недействительна")

    now_utc = datetime.utcnow()
    if session.login_at and (now_utc - session.login_at.replace(tzinfo=None)) > timedelta(hours=24):
        session.status = "expired"
        db.commit()
        print(f"Session EXPIRED: {session.user_login}")
        raise HTTPException(401, "Сессия истекла (24 часа)")

    user = db.query(User).filter(User.login == session.user_login).first()
    if not user:
        print(f"User NOT FOUND: {session.user_login}")
        raise HTTPException(401, "Пользователь не найден")

    print(f"get_current_user: {user.login}")
    return user