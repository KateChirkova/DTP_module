from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

class Base(DeclarativeBase):
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DB_FILE = PROJECT_ROOT / "data" / "database.sqlite"

engine = create_engine(f"sqlite:///{DB_FILE}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()