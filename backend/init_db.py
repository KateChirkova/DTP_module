from src.traffic_dtp.db.session import engine, Base
from src.traffic_dtp.db.models import User, Detection, Accident, Notification, UserSession  # models/__init__.py

Base.metadata.create_all(bind=engine)

# Проверка
from sqlalchemy import text
with engine.connect() as conn:
    tables = [row[0] for row in conn.execute(text('SELECT name FROM sqlite_master WHERE type="table";')).fetchall()]
print("Таблицы:", tables)

def migrate_tables(engine):
    # Добавила колонки для формата
    with engine.connect() as conn:
        columns = [
            ("detections", "bbox_x1", "INTEGER"),
            ("detections", "bbox_y1", "INTEGER"),
            ("detections", "bbox_x2", "INTEGER"),
            ("detections", "bbox_y2", "INTEGER"),
            ("detections", "accident_id", "INTEGER"),
        ]

        for table, col, type_ in columns:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {type_}"))
                print(f"✅ Добавлена {table}.{col}")
            except:
                print(f"⏭️ {table}.{col} уже существует")

        conn.commit()

Base.metadata.create_all(bind=engine)
migrate_tables(engine)