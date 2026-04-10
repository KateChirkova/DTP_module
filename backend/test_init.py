#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.traffic_dtp.db.session import Base
from src.traffic_dtp.db.models.user import User

print("🔍 User.__mro__:", User.__mro__)
print("🔍 User.__tablename__:", getattr(User, '__tablename__', 'НЕТ!'))
print("🔍 Base.metadata.tables:", list(Base.metadata.tables.keys()))

try:
    User.metadata  # Проверяем регистрацию
    print("User ок")
except Exception as e:
    print("User сломана:", e)