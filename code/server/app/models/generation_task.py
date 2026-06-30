"""
生成任务 ORM
"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Integer, SmallInteger, Boolean, DateTime, Text, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, new_uuid, utcnow


class GenerationTask(Base):
    __tablename__ = "generation_tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("generation_groups.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    image_asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("image_assets.id", ondelete="RESTRICT"), nullable=False)

    # Input snapshots at generation time
    tag_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    model_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    negative_prompt: Mapped[str | None] = mapped_column(Text, default="")

    # Parameters
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    resolution: Mapped[str] = mapped_column(String(10), nullable=False)
    extended_params: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    # External API info
    api_task_id: Mapped[str | None] = mapped_column(String(255))
    api_provider: Mapped[str | None] = mapped_column(String(50))

    # Output
    status: Mapped[str] = mapped_column(String(20), default="queued")
    result_video_key: Mapped[str | None] = mapped_column(String(500))
    result_thumbnail_key: Mapped[str | None] = mapped_column(String(500))
    error_message: Mapped[str | None] = mapped_column(Text)

    # Quality assessment
    quality_score: Mapped[int | None] = mapped_column(SmallInteger)
    quality_notes: Mapped[str | None] = mapped_column(Text)
    is_best_attempt: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metadata
    attempt_number: Mapped[int] = mapped_column(SmallInteger, default=1)
    generation_time_seconds: Mapped[int | None] = mapped_column(Integer)
    cost_yuan: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
