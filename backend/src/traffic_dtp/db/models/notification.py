from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.traffic_dtp.db.session import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    accident_id = Column(Integer, ForeignKey("accidents.id"), nullable=False)

    status = Column(String(20), default="unread")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_sent = Column(Boolean, default=False)

    user_login = Column(String(50), ForeignKey("user.login"), nullable=False, index=True)

    accident = relationship("Accident", back_populates="notifications")
    user = relationship("User", back_populates="notifications")