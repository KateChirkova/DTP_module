from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.traffic_dtp.db.session import SessionLocal, Base
from src.traffic_dtp.db.models.user import User
import hashlib, jwt

router = APIRouter(prefix="/v1/auth")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/login")
async def login(login: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login == login).first()
    if not user or hashlib.sha256(password.encode()).hexdigest() != user.password_hash:
        raise HTTPException(401, "Invalid")
    token = jwt.encode({"sub": login}, "secret", algorithm="HS256")
    return {"success": True, "token": token, "expires_in": 86400}