#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.traffic_dtp.services.auth import hash_password
from src.traffic_dtp.db.session import SessionLocal
from src.traffic_dtp.db.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.login == "kate").first()
if not user:
    user = User(login="kate", password_hash=hash_password("123456"))
    db.add(user)
    db.commit()
    print("Kate:123456 добавлен")
db.close()