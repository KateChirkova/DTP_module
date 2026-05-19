from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.traffic_dtp.db.session import Base


# одно уведомление на ДТП; прочтение — в notification_reads
class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (UniqueConstraint("accident_id", name="uq_notifications_accident_id"),)

    id = Column(Integer, primary_key=True)
    accident_id = Column(Integer, ForeignKey("accidents.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    accident = relationship("Accident", back_populates="notifications")
    reads = relationship(
        "NotificationRead",
        back_populates="notification",
        cascade="all, delete-orphan",
    )
