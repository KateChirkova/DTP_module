from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from src.traffic_dtp.db.session import Base

class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True)
    user_login = Column(String(50), ForeignKey("user.login"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String)
    login_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    logout_at = Column(DateTime(timezone=True))
    status = Column(String(20), nullable=False, default="active")