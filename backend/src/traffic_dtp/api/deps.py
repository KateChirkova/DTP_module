from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.traffic_dtp.db.models.user import User
from src.traffic_dtp.db.session import get_db
from src.traffic_dtp.services import user_session as session_service

security = HTTPBearer()


# накладка Bearer-токена на пользователя (сессия в БД)
def _resolve_user_from_token(db: Session, token: str) -> User:
    session = session_service.find_active_session_by_token(db, token)

    if not session:
        raise HTTPException(status_code=401, detail="Сессия недействительна")

    if session_service.is_session_expired(session):
        session_service.expire_session(db, session)
        raise HTTPException(status_code=401, detail="Сессия истекла (24 часа)")

    user = db.query(User).filter(User.login == session.user_login).first()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    return user


def get_current_user(
    authorization=Depends(security),
    db: Session = Depends(get_db),
) -> User:
    return _resolve_user_from_token(db, authorization.credentials)


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    return user


def get_user_for_ws_token(token: str, db: Session) -> User:
    return _resolve_user_from_token(db, token)
