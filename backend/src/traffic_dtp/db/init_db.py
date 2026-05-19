# create_all для всех ORM-моделей
from src.traffic_dtp.db import models  # noqa: F401
from src.traffic_dtp.db.session import Base, engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database initialized")
