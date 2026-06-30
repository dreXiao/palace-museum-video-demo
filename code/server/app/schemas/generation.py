"""
生成相关 Pydantic Schema
"""
from datetime import datetime
from decimal import Decimal
from typing import Any
from pydantic import BaseModel, Field


# ── Request ──

class GenerationSubmitRequest(BaseModel):
    image_asset_id: str
    tag_ids: list[str] = Field(min_length=1, max_length=6)
    model_id: str
    duration: int = Field(ge=2, le=16, default=10)
    resolution: str = "1080p"
    extended_params: dict[str, Any] = Field(default_factory=dict)


class BatchSubmitRequest(BaseModel):
    image_asset_id: str
    tag_ids: list[str] = Field(min_length=1, max_length=6)
    model_ids: list[str] = Field(min_length=1, max_length=3)
    duration: int = 10
    resolution: str = "1080p"
    extended_params: dict[str, Any] = Field(default_factory=dict)


class TaskRateRequest(BaseModel):
    quality_score: int = Field(ge=1, le=5)
    quality_notes: str | None = None


# ── Response ──

class GenerationTaskOut(BaseModel):
    id: str
    group_id: str
    user_id: str
    image_asset_id: str
    tag_snapshot: dict
    model_snapshot: dict
    prompt: str
    negative_prompt: str | None = None
    duration: int
    resolution: str
    status: str
    result_video_url: str | None = None
    result_thumbnail_url: str | None = None
    error_message: str | None = None
    quality_score: int | None = None
    quality_notes: str | None = None
    is_best_attempt: bool = False
    attempt_number: int
    generation_time_seconds: int | None = None
    cost_yuan: Decimal | None = None
    created_at: str
    completed_at: str | None = None

    model_config = {"from_attributes": True}


class GenerationGroupOut(BaseModel):
    id: str
    image_asset_id: str
    tag_id: str
    model_id: str
    user_id: str
    best_attempt_id: str | None = None
    total_attempts: int = 0
    total_cost_yuan: Decimal | None = 0
    created_at: str
    updated_at: str
    # 关联数据
    image_asset: dict | None = None
    tag: dict | None = None
    model: dict | None = None
    best_attempt: dict | None = None

    model_config = {"from_attributes": True}
