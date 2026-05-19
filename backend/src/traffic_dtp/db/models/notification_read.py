from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.traffic_dtp.db.session import Base


# факт прочтения уведомления конкретным пользователем
class NotificationRead(Base):
    __tablename__ = "notification_reads"
    __table_args__ = (
        UniqueConstraint("notification_id", "user_login", name="uq_notification_read_user"),
    )

    id = Column(Integer, primary_key=True)
    notification_id = Column(
        Integer,
        ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_login = Column(String(50), ForeignKey("user.login"), nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    notification = relationship("Notification", back_populates="reads")
    user = relationship("User", back_populates="notification_reads")
