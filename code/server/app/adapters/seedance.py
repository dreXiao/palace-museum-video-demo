"""
豆包 Seedance (火山引擎 ARK) API 适配器
"""
from typing import Any
from app.adapters.base import BaseAdapter, GenerationResult, TaskStatus


class SeedanceAdapter(BaseAdapter):
    """火山引擎 ARK — Seedance 2.0 图生视频"""

    SUBMIT_PATH = "/api/v3/video/generations"
    QUERY_PATH = "/api/v3/video/generations/{task_id}"

    STATUS_MAP = {
        "queued": "queued",
        "processing": "processing",
        "succeeded": "completed",
        "failed": "failed",
        "canceled": "failed",
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

        body = {
            "model": model_id,
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": prompt},
            ],
            "parameters": {
                "duration": duration,
                "size": self._size_for_resolution(resolution),
                "seed": params.get("seed", -1),
                "watermark": params.get("watermark", False),
            },
        }

        if negative_prompt:
            body["parameters"]["negative_prompt"] = negative_prompt

        if "cfg_scale" in params:
            body["parameters"]["cfg_scale"] = params["cfg_scale"]

        try:
            data = await self._post(self.SUBMIT_PATH, body)
            task_id = data.get("id", "")
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
            data = await self._get(self.QUERY_PATH.format(task_id=api_task_id))
            api_status = data.get("status", "failed")
            status = self.STATUS_MAP.get(api_status, "failed")
            return TaskStatus(
                status=status,
                video_url=data.get("video_url") if status == "completed" else None,
                error_message=data.get("error", {}).get("message") if status == "failed" else None,
                progress=data.get("progress", 0),
            )
        except Exception as e:
            return TaskStatus(status="failed", error_message=str(e))

    async def test_connection(self) -> tuple[bool, str]:
        try:
            await self._post(self.SUBMIT_PATH, {"model": list(self.config.model_ids.values())[0], "content": [], "parameters": {}})
            return True, "Connected"
        except Exception as e:
            err = str(e)
            if "401" in err or "403" in err or "Unauthorized" in err:
                return False, "API Key 无效"
            return False, str(e)[:200]

    @staticmethod
    def _size_for_resolution(res: str) -> str:
        return {"480p": "720x480", "720p": "1280x720", "1080p": "1920x1080", "2k": "2560x1440"}.get(res, "1920x1080")
