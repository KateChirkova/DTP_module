from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from src.traffic_dtp.db.session import Base

class User(Base):
    __tablename__ = "user"
    login = Column(String(50), primary_key=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())