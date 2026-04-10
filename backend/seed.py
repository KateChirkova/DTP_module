from src.traffic_dtp.db.session import SessionLocal
from src.traffic_dtp.db.models.user import User
from src.traffic_dtp.db.models.accident import Accident
from datetime import datetime

db = SessionLocal()
user = User(login="kate", password_hash="$2b$12$...")  # bcrypt "123456"
db.add(user)

acc = Accident(status="active", first_seen=datetime.now(), last_seen=datetime.now(), geo_lat=55.7558, geo_lon=37.6173, confidence=0.92)  # Москва ДТП
db.add(acc)
db.commit()
print("Kate + 1 accident")