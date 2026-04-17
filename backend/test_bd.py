#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.traffic_dtp.db.session import engine, Base
print("Engine:", engine.url)

print("До импорта моделей:", list(Base.metadata.tables.keys()))

try:
    from src.traffic_dtp.db.models.user import User
    print("User импортирована")
except Exception as e:
    print("User:", e); raise

print("После импорта:", list(Base.metadata.tables.keys()))

Base.metadata.create_all(bind=engine)
print("create_all выполнен")

# Проверка
from sqlalchemy import text
with engine.connect() as conn:
    tables = [row[0] for row in conn.execute(text('SELECT name FROM sqlite_master WHERE type="table";')).fetchall()]
    print("Итог:", tables)