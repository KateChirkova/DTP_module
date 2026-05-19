# CLI: python init_db.py из каталога backend
from src.traffic_dtp.db.init_db import init_db

if __name__ == "__main__":
    init_db()
    print("Database initialized")
