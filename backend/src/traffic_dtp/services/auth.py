import hashlib
import time
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(login: str) -> str:
    payload = f"{login}:{int(time.time())}"
    return hashlib.sha256(payload.encode()).hexdigest()

def verify_token(token: str, login: str) -> bool:
    expected = create_token(login)
    return token == expected and (time.time() - int(token[-16:], 16)) < 86400