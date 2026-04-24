from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import hashlib

from src.traffic_dtp.db.session import get_db
from src.traffic_dtp.db.models.user import User

router = APIRouter(prefix="/api", tags=["auth"])

class LoginRequest(BaseModel):
    login: str
    password: str

@router.post("/v1/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login == req.login).first()

    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    password_hash = hashlib.sha256(req.password.encode()).hexdigest()

    if user.password_hash != password_hash:
        raise HTTPException(status_code=401, detail="Неверный пароль")

    return {
        "success": True,
        "token": f"jwt-{req.login}-2026",
        "expires_in": 86400,
    }