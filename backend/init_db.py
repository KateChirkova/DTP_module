from src.traffic_dtp.db.session import engine, Base
from src.traffic_dtp.db.models import User, Detection, Accident, Notification, UserSession  # models/__init__.py

Base.metadata.create_all(bind=engine)

# Проверка
from sqlalchemy import text
with engine.connect() as conn:
    tables = [row[0] for row in conn.execute(text('SELECT name FROM sqlite_master WHERE type="table";')).fetchall()]
print("Таблицы:", tables)