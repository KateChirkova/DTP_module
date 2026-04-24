from src.traffic_dtp.db.session import engine, Base
from src.traffic_dtp.db.models import User, Detection, Accident, Notification, UserSession

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized")