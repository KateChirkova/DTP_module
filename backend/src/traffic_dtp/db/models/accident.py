from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.traffic_dtp.db.session import Base


class Accident(Base):
    __tablename__ = "accidents"

    id = Column(Integer, primary_key=True)

    bbox_x1 = Column(Integer)
    bbox_y1 = Column(Integer)
    bbox_x2 = Column(Integer)
    bbox_y2 = Column(Integer)

    confidence = Column(Float)
    missed_screenshots = Column(Integer, default=0)

    first_seen = Column(DateTime(timezone=True))
    last_seen = Column(DateTime(timezone=True))
    status_updated_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    event_status = Column(String(20), default="created")
    is_active = Column(Boolean, default=True)

    detections = relationship("Detection", back_populates="accident")
    notifications = relationship("Notification", back_populates="accident")