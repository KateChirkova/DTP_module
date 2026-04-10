from sqlalchemy import Column, Integer, DECIMAL, ForeignKey, DateTime, String
from sqlalchemy.sql import func
from src.traffic_dtp.db.session import Base

class Detection(Base):
    __tablename__ = "detections"
    id = Column(Integer, primary_key=True, autoincrement=True)
    screenshot_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    confidence = Column(String(5), nullable=False)
    bbox_x1 = Column(Integer, nullable=False)
    bbox_y1 = Column(Integer, nullable=False)
    bbox_x2 = Column(Integer, nullable=False)
    bbox_y2 = Column(Integer, nullable=False)
    geo_lat = Column(String(10), nullable=False)
    geo_lon = Column(String(11), nullable=False)
    accident_id = Column(Integer, ForeignKey("accidents.id"))