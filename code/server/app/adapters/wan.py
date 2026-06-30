"""
通义万相 DashScope API 适配器
"""
from typing import Any
from app.adapters.base import BaseAdapter, GenerationResult, TaskStatus


class WanAdapter(BaseAdapter):
    """DashScope 通义万相 图生视频适配器"""

    SUBMIT_PATH = "/api/v1/services/aigc/video-generation/video-synthesis"
    QUERY_PATH = "/api/v1/tasks/{task_id}"

    STATUS_MAP = {
        "PENDING": "queued",
        "RUNNING": "processing",
        "SUCCEEDED": "completed",
        "FAILED": "failed",
        "CANCELED": "failed",
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
            "input": {
                "prompt": prompt,
                "media": [{"type": "first_frame", "url": image_url}],
            },
            "parameters": {
                "resolution": resolution,
                "duration": duration,
                "prompt_extend": params.get("prompt_extend", True),
                "watermark": params.get("watermark", False),
            },
        }

        # Add optional extended params to parameters
        for key in ("seed", "guidance_scale", "num_inference_steps"):
            if key in params and params[key] is not None:
                body["parameters"][key] = params[key]

        if negative_prompt:
            body["input"]["negative_prompt"] = negative_prompt

        try:
            data = await self._post(
                self.SUBMIT_PATH,
                body,
                headers={**self._default_headers(), "X-DashScope-Async": "enable"},
            )
            task_id = data.get("output", {}).get("task_id", "")
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
            output = data.get("output", {})
            api_status = output.get("task_status", "FAILED")
            status = self.STATUS_MAP.get(api_status, "failed")
            return TaskStatus(
                status=status,
                video_url=output.get("video_url") if status == "completed" else None,
                error_message=output.get("message") if status == "failed" else None,
                progress=100 if status == "completed" else (50 if status == "processing" else 0),
            )
        except Exception as e:
            return TaskStatus(status="failed", error_message=str(e))

    async def test_connection(self) -> tuple[bool, str]:
        try:
            # Test with a simple model info call instead of an actual generation
            await self._post(self.SUBMIT_PATH, {"model": list(self.config.model_ids.values())[0], "input": {}, "parameters": {}}, headers={**self._default_headers(), "X-DashScope-Async": "enable"})
            return True, "Connected"
        except Exception as e:
            err = str(e)
            if "401" in err or "403" in err:
                return False, "API Key 无效"
            return False, str(e)[:200]
