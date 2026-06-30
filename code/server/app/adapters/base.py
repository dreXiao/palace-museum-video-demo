"""
API 适配器抽象基类
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import os
import httpx
from app.models.model_config import ModelConfig


@dataclass
class GenerationResult:
    success: bool
    task_id: str | None = None
    video_url: str | None = None
    error_message: str | None = None
    estimated_cost: float = 0.0


@dataclass
class TaskStatus:
    status: str  # queued | processing | completed | failed
    video_url: str | None = None
    error_message: str | None = None
    progress: int = 0


class BaseAdapter(ABC):
    """图生视频 API 适配器基类"""

    def __init__(self, config: ModelConfig):
        self.config = config

    def _get_api_key(self) -> str:
        key = os.getenv(self.config.api_key_env, "")
        if not key:
            raise ValueError(f"API Key not found in env: {self.config.api_key_env}")
        return key

    @abstractmethod
    async def submit(
        self,
        image_url: str,
        prompt: str,
        negative_prompt: str = "",
        duration: int = 10,
        resolution: str = "1080p",
        extended_params: dict[str, Any] | None = None,
    ) -> GenerationResult:
        """提交生成任务到外部 API"""
        ...

    @abstractmethod
    async def query_task(self, api_task_id: str) -> TaskStatus:
        """查询任务状态"""
        ...

    @abstractmethod
    async def test_connection(self) -> tuple[bool, str]:
        """测试 API 连通性"""
        ...

    async def _post(self, path: str, body: dict, headers: dict | None = None) -> dict:
        url = f"{self.config.endpoint.rstrip('/')}{path}"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=body, headers=headers or self._default_headers())
            resp.raise_for_status()
            return resp.json()

    async def _get(self, path: str, headers: dict | None = None) -> dict:
        url = f"{self.config.endpoint.rstrip('/')}{path}"
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=headers or self._default_headers())
            resp.raise_for_status()
            return resp.json()

    def _default_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._get_api_key()}",
        }
