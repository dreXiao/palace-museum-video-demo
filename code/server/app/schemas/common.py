"""
通用 Pydantic Schema — 分页 / 响应信封
"""
from typing import Any, Generic, TypeVar
from pydantic import BaseModel


class PaginationMeta(BaseModel):
    cursor: str | None = None
    has_more: bool = False
    total: int = 0


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    message: str | None = None
    pagination: PaginationMeta | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    data: None = None
    message: str
    error_code: str = "APP_ERROR"
