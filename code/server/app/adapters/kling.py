"""
可灵 Kling API 适配器
"""
import os
import time
import jwt as pyjwt
from typing import Any
from app.adapters.base import BaseAdapter, GenerationResult, TaskStatus


class KlingAdapter(BaseAdapter):
    """Kling 开放平台 图生视频"""

    SUBMIT_PATH = "/v1/videos/image2video"
    QUERY_PATH = "/v1/videos/image2video/{task_id}"

    STATUS_MAP = {
        "submitted": "queued",
        "processing": "processing",
        "succeed": "completed",
        "failed": "failed",
    }

    def _get_auth_headers(self) -> dict[str, str]:
        """Kling 使用 JWT Token 认证"""
        ak = self._get_api_key()
        sk = os.getenv("KLING_API_SECRET", "")
        if not sk:
            raise ValueError("KLING_API_SECRET not configured in env")

        payload = {
            "access_key": ak,
            "iss": "kling",
            "iat": int(time.time()),
            "exp": int(time.time()) + 1800,
            "nbf": int(time.time()),
        }
        token = pyjwt.encode(payload, sk, algorithm="HS256")
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

    async def submit(
        self,
        image_url: str,
        prompt: str,
        negative_prompt: str = "",
        duration: int = 10,
        resolution: str = "1080p",
        extended_params: dict[str, Any] | None = None,
    ) -> GenerationResult:
        model_id = self.config.model_ids.get(resolution) or self.config.model_ids.get("1080p", "")
        params: dict[str, Any] = extended_params or {}
        mode = params.get("mode", "std")

        body = {
            "model_name": model_id,
            "mode": mode,
            "duration": str(duration),
            "image": image_url,
            "prompt": prompt,
            "cfg_scale": params.get("cfg_scale", 0.5),
        }

        if negative_prompt:
            body["negative_prompt"] = negative_prompt

        try:
            data = await self._post(self.SUBMIT_PATH, body, headers=self._get_auth_headers())
            task_id = data.get("data", {}).get("task_id", "")
            rate = self.config.pricing.get("rates", {}).get(resolution, 0)
            return GenerationResult(
                success=bool(task_id),
                task_id=task_id,
                estimated_cost=rate * duration,
            )
        except Exception as e:
            return GenerationResult(success=False, error_message=str(e))

    async def query_task(self, api_task_id: str) -> TaskStatus:
        try:
            data = await self._get(self.QUERY_PATH.format(task_id=api_task_id), headers=self._get_auth_headers())
            task_data = data.get("data", {})
            api_status = task_data.get("task_status", "failed")
            status = self.STATUS_MAP.get(api_status, "failed")

            task_result = task_data.get("task_result", {}) or {}
            videos = task_result.get("videos", [])
            video_url = videos[0].get("url") if videos else None

            return TaskStatus(
                status=status,
                video_url=video_url,
                error_message=task_data.get("task_status_msg") if status == "failed" else None,
                progress=100 if status == "completed" else (50 if status == "processing" else 0),
            )
        except Exception as e:
            return TaskStatus(status="failed", error_message=str(e))

    async def test_connection(self) -> tuple[bool, str]:
        try:
            headers = self._get_auth_headers()
            await self._get(self.QUERY_PATH.format(task_id="test"), headers=headers)
            return True, "Connected"
        except Exception as e:
            err = str(e)
            if "401" in err or "403" in err or "Unauthorized" in err:
                return False, "API Key/Secret 无效"
            return False, str(e)[:200]
