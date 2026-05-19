from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from src.traffic_dtp.db.session import Base


# серверная сессия: active | closed | expired
class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True)
    user_login = Column(String(50), ForeignKey("user.login"), nullable=False)
    token_hash = Column(String(64), unique=True, nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(512), nullable=False, default="unknown")
    login_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    logout_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default="active", server_default="active")