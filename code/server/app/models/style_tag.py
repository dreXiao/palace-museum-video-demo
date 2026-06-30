"""
标签与标签版本 ORM
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, new_uuid, utcnow


class StyleTag(Base):
    __tablename__ = "style_tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#6366F1")
    icon: Mapped[str] = mapped_column(String(10), default="🎨")
    description: Mapped[str | None] = mapped_column()
    applicable_types: Mapped[list | None] = mapped_column(ARRAY(Text))
    positive_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    negative_prompt: Mapped[str | None] = mapped_column(Text, default="")
    variables: Mapped[list | None] = mapped_column(ARRAY(Text), default=list)
    default_params: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    is_preset: Mapped[bool] = mapped_column(Boolean, default=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class StyleTagVersion(Base):
    __tablename__ = "style_tag_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("style_tags.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    change_note: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
