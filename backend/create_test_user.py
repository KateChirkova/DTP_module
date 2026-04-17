#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.traffic_dtp.db.session import SessionLocal
from src.traffic_dtp.db.models.user import User
import hashlib

db = SessionLocal()

user = db.query(User).filter(User.login == "kate").first()
if user:
    db.delete(user)
    db.commit()
    print("Старый акк удален")

# ✅ Создай новую (SHA256)
password_hash = hashlib.sha256("123456".encode()).hexdigest()
print(f"🔑 SHA256 хэш: {password_hash[:20]}...")

user = User(login="kate", password_hash=password_hash)
db.add(user)
db.commit()
print("✅ Kate:123456 (SHA256) создан")

db.close()