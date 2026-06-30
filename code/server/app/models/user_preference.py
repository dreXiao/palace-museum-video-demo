"""
用户偏好 ORM
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    default_model_id: Mapped[uuid.UUID | None] = mapped_column()
    default_resolution: Mapped[str] = mapped_column(String(10), default="1080p")
    default_duration: Mapped[int] = mapped_column(Integer, default=10)
    history_view: Mapped[str] = mapped_column(String(10), default="grid")
    page_size: Mapped[int] = mapped_column(Integer, default=20)
    language: Mapped[str] = mapped_column(String(10), default="zh-CN")
    theme: Mapped[str] = mapped_column(String(10), default="system")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
