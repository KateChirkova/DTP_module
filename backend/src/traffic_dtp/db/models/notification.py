from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.traffic_dtp.db.session import Base

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    accident_id = Column(Integer, ForeignKey("accidents.id"), nullable=False)
    status = Column(String(10), nullable=False, default="unread")
    event = Column(String(20), nullable=False)
    accident_status = Column(String(20), nullable=False)