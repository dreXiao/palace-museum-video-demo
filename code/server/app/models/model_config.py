"""
模型配置 ORM
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, new_uuid, utcnow


class ModelConfig(Base):
    __tablename__ = "model_configs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column()
    api_type: Mapped[str] = mapped_column(String(30), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key_env: Mapped[str] = mapped_column(String(100), nullable=False)
    model_ids: Mapped[dict] = mapped_column(JSONB, default=dict)
    parameters: Mapped[dict] = mapped_column(JSONB, default=dict)
    pricing: Mapped[dict] = mapped_column(JSONB, default=dict)
    generation_config: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_preset: Mapped[bool] = mapped_column(Boolean, default=False)
    connection_status: Mapped[str] = mapped_column(String(20), default="untested")
    last_tested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
