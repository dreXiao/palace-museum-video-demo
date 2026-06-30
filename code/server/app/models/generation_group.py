"""
生成分组 ORM
"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Integer, SmallInteger, Boolean, DateTime, Text, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, new_uuid, utcnow


class GenerationGroup(Base):
    __tablename__ = "generation_groups"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    image_asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("image_assets.id", ondelete="RESTRICT"), nullable=False)
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("style_tags.id", ondelete="RESTRICT"), nullable=False)
    model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("model_configs.id", ondelete="RESTRICT"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    best_attempt_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("generation_tasks.id", ondelete="SET NULL"))
    total_attempts: Mapped[int] = mapped_column(SmallInteger, default=0)
    total_cost_yuan: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
