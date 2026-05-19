from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.traffic_dtp.db.session import Base


# учётная запись оператора (логин = PK)
class User(Base):
    __tablename__ = "user"
    login = Column(String(50), primary_key=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    notification_reads = relationship("NotificationRead", back_populates="user")
