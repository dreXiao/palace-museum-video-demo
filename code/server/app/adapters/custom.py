"""
通用自定义适配器 — JSON 配置驱动的 HTTP 适配器
支持通过请求/响应映射字段接入任意 REST API
"""
import re
from typing import Any
from app.adapters.base import BaseAdapter, GenerationResult, TaskStatus


class CustomAdapter(BaseAdapter):
    """
    通过模型配置中的 customAdapter 字段驱动请求/响应映射。
    无需写 Python 代码，纯 JSON 配置即可接入新 API。
    """

    def _get_template_value(self, template: str, variables: dict[str, Any]) -> str:
        result = template
        for key, val in variables.items():
            result = result.replace(f"{{{key}}}", str(val))
        return result

    def _resolve_path(self, path_or_template: str, variables: dict[str, Any]) -> str:
        return self._get_template_value(path_or_template, variables)

    def _build_body(self, mapping: dict, variables: dict[str, Any]) -> dict:
        """递归构建请求体，支持模板变量"""
        result: dict[str, Any] = {}
        for target_key, source_key in mapping.items():
            if isinstance(source_key, dict):
                result[target_key] = self._build_body(source_key, variables)
            elif isinstance(source_key, str):
                # If looks like a template, resolve; otherwise literal
                val = self._get_template_value(source_key, variables) if "{" in source_key else source_key
                result[target_key] = val
            else:
                result[target_key] = source_key
        return result

    async def submit(
        self,
        image_url: str,
        prompt: str,
        negative_prompt: str = "",
        duration: int = 10,
        resolution: str = "1080p",
        extended_params: dict[str, Any] | None = None,
    ) -> GenerationResult:
        custom = self.config.model_ids
        adapter_cfg = self.config.model_ids if hasattr(self.config, 'adapter_config') else None

        # Fallback: use api paths from generation_config or modelIds for custom adapter
        gen_cfg = self.config.generation_config or {}
        adapter_cfg = gen_cfg.get("customAdapter")
        if not adapter_cfg:
            return GenerationResult(success=False, error_message="Custom adapter not configured in generation_config.customAdapter")

        submit_path = adapter_cfg.get("submitPath", "/v1/generate")
        rq_map = adapter_cfg.get("requestMapping", {})

        variables = {
            "image_url": image_url,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "duration": duration,
            "resolution": resolution,
            "apiKey": self._get_api_key(),
            **(extended_params or {}),
        }

        # Build auth header from template
        auth_template = adapter_cfg.get("authHeader", "Bearer {apiKey}")
        auth_value = self._get_template_value(auth_template, variables)
        headers = {"Content-Type": "application/json", "Authorization": auth_value}

        # Add async header if configured
        async_h = adapter_cfg.get("asyncHeader")
        if async_h:
            headers[async_h["name"]] = async_h["value"]

        body = self._build_body(rq_map, variables)

        try:
            data = await self._post(submit_path, body, headers=headers)
            resp_map = adapter_cfg.get("responseMapping", {})
            task_id_path = resp_map.get("taskIdPath", "task_id")
            task_id = str(self._extract_nested(data, task_id_path))

            rate = self.config.pricing.get("rates", {}).get(resolution, 0)
            return GenerationResult(
                success=bool(task_id),
                task_id=task_id,
                estimated_cost=rate * duration,
            )
        except Exception as e:
            return GenerationResult(success=False, error_message=str(e))

    async def query_task(self, api_task_id: str) -> TaskStatus:
        gen_cfg = self.config.generation_config or {}
        adapter_cfg = gen_cfg.get("customAdapter", {})
        query_path_template = adapter_cfg.get("queryPath", "/v1/tasks/{task_id}")
        query_path = self._resolve_path(query_path_template, {"task_id": api_task_id})

        headers = {"Authorization": self._get_template_value(adapter_cfg.get("authHeader", "Bearer {apiKey}"), {"apiKey": self._get_api_key()})}

        try:
            data = await self._get(query_path, headers=headers)
            resp_map = adapter_cfg.get("responseMapping", {})
            status_path = resp_map.get("statusPath", "status")
            video_url_path = resp_map.get("videoUrlPath", "video_url")
            status_map_key = resp_map.get("statusMap", {})

            api_status = str(self._extract_nested(data, status_path))
            status = status_map_key.get(api_status, "failed") if status_map_key else "completed" if api_status else "failed"

            return TaskStatus(
                status=status,
                video_url=str(self._extract_nested(data, video_url_path)) if status == "completed" else None,
                progress=100 if status == "completed" else 50,
            )
        except Exception as e:
            return TaskStatus(status="failed", error_message=str(e))

    async def test_connection(self) -> tuple[bool, str]:
        try:
            await self._get("/", headers=self._default_headers())
            return True, "Connected"
        except Exception as e:
            return False, str(e)[:200]

    @staticmethod
    def _extract_nested(data: dict, path: str) -> Any:
        """Extract nested value from dict using dot-path"""
        key = path
        val: Any = data
        for part in key.split("."):
            if isinstance(val, dict):
                val = val.get(part)
            elif isinstance(val, list) and part.isdigit():
                val = val[int(part)]
            else:
                return None
        return val
