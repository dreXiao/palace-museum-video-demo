"""
标签相关 Pydantic Schema
"""
from pydantic import BaseModel, Field
from typing import Any


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    color: str = Field(default="#6366F1", max_length=7)
    icon: str = Field(default="🎨", max_length=10)
    description: str | None = None
    applicable_types: list[str] = Field(default_factory=list)
    positive_prompt: str = Field(min_length=1)
    negative_prompt: str = ""
    variables: list[str] = Field(default_factory=list)
    default_params: dict[str, Any] = Field(default_factory=dict)


class TagUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    icon: str | None = None
    description: str | None = None
    applicable_types: list[str] | None = None
    positive_prompt: str | None = None
    negative_prompt: str | None = None
    variables: list[str] | None = None
    default_params: dict[str, Any] | None = None
    change_note: str | None = None  # Version change note


class TagOut(BaseModel):
    id: str
    name: str
    color: str
    icon: str
    description: str | None = None
    applicable_types: list[str] | None = None
    positive_prompt: str
    negative_prompt: str | None = None
    variables: list[str] | None = None
    default_params: dict | None = None
    is_preset: bool = False
    usage_count: int = 0
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class TagVersionOut(BaseModel):
    id: str
    tag_id: str
    version_number: int
    snapshot: dict
    change_note: str | None = None
    created_at: str

    model_config = {"from_attributes": True}
