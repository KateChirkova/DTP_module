from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from src.traffic_dtp.db.session import Base

class Accident(Base):
    __tablename__ = "accidents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), nullable=False, default="active")
    first_seen = Column(DateTime(timezone=True), nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=False)
    geo_lat = Column(String(10), nullable=False)
    geo_lon = Column(String(11), nullable=False)
    confidence = Column(String(5), nullable=False)
    missed_screenshots = Column(Integer, default=0)