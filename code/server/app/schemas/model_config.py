"""
模型配置相关 Pydantic Schema
"""
from pydantic import BaseModel, Field
from typing import Any


class ModelConfigCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    provider: str = Field(min_length=1, max_length=50)
    description: str | None = None
    api_type: str = "custom"
    endpoint: str
    api_key_env: str = Field(min_length=1, max_length=100)
    model_ids: dict[str, str] = Field(default_factory=dict)
    parameters: dict[str, Any] = Field(default_factory=dict)
    pricing: dict[str, Any] = Field(default_factory=dict)
    generation_config: dict[str, Any] = Field(default_factory=dict)


class ModelConfigUpdate(BaseModel):
    name: str | None = None
    provider: str | None = None
    description: str | None = None
    api_type: str | None = None
    endpoint: str | None = None
    api_key_env: str | None = None
    model_ids: dict[str, str] | None = None
    parameters: dict[str, Any] | None = None
    pricing: dict[str, Any] | None = None
    generation_config: dict[str, Any] | None = None


class ModelConfigOut(BaseModel):
    id: str
    name: str
    provider: str
    description: str | None = None
    api_type: str
    endpoint: str
    api_key_env: str
    model_ids: dict
    parameters: dict
    pricing: dict
    generation_config: dict | None = None
    is_default: bool = False
    is_preset: bool = False
    connection_status: str = "untested"
    last_tested_at: str | None = None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}
