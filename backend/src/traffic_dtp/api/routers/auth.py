from fastapi import APIRouter, Depends, HTTPException
from src.traffic_dtp.schemas.auth import LoginRequest
from src.traffic_dtp.services.auth import create_jwt_token
router = APIRouter(prefix="/v1/auth")

@router.post("/login")
async def login(request: LoginRequest):
    user = db.query(User).filter(User.login == request.login).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_jwt_token({"sub": user.login})
    return {"success": True, "token": token, "expires_in": 86400}