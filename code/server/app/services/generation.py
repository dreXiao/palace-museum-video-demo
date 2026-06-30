"""
视频生成服务 — 核心业务流程编排
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.model_config import ModelConfig
from app.models.style_tag import StyleTag
from app.models.image_asset import ImageAsset
from app.models.generation_task import GenerationTask
from app.models.generation_group import GenerationGroup
from app.adapters.registry import AdapterRegistry
from app.core.exceptions import ModelNotConnectedError, ModelApiKeyMissingError, NotFoundError
from app.core.storage import storage_service


class GenerationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def submit(
        self,
        user_id: str,
        image_asset_id: str,
        tag_id: str,
        model_id: str,
        duration: int = 10,
        resolution: str = "1080p",
        extended_params: dict[str, Any] | None = None,
    ) -> GenerationTask:
        """Submit a single generation task"""
        user_uuid = uuid.UUID(user_id)

        # Load configs
        model_config = await self._get_model(model_id)
        tag = await self._get_tag(tag_id)
        image_asset = await self._get_image(image_asset_id)

        if model_config.connection_status != "connected":
            raise ModelNotConnectedError(model_config.name)

        # Build prompt from tag template
        prompt = self._build_prompt(tag.positive_prompt, image_asset.metadata or {})

        # Create adapter and submit to external API
        adapter = AdapterRegistry.create(model_config)
        try:
            result = await adapter.submit(
                image_url=image_asset.storage_url,
                prompt=prompt,
                negative_prompt=tag.negative_prompt or "",
                duration=duration,
                resolution=resolution,
                extended_params=extended_params,
            )
        except ValueError as e:
            raise ModelApiKeyMissingError(model_config.name, model_config.api_key_env) from e

        # Find or create group
        group = await self._find_or_create_group(user_uuid, image_asset_id, tag_id, model_id)
        attempt_number = group.total_attempts + 1

        # Create task
        task = GenerationTask(
            id=uuid.uuid4(),
            group_id=group.id,
            user_id=user_uuid,
            image_asset_id=uuid.UUID(image_asset_id),
            tag_snapshot={
                "id": str(tag.id), "name": tag.name, "positive_prompt": tag.positive_prompt,
                "negative_prompt": tag.negative_prompt, "color": tag.color, "icon": tag.icon,
            },
            model_snapshot={
                "id": str(model_config.id), "name": model_config.name, "provider": model_config.provider,
                "api_type": model_config.api_type, "pricing": model_config.pricing,
            },
            prompt=prompt,
            negative_prompt=tag.negative_prompt,
            duration=duration,
            resolution=resolution,
            extended_params=extended_params or {},
            status="generating",
            api_task_id=result.task_id,
            api_provider=model_config.api_type,
            attempt_number=attempt_number,
            cost_yuan=Decimal(str(result.estimated_cost)),
        )
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def submit_batch(
        self,
        user_id: str,
        image_asset_id: str,
        tag_ids: list[str],
        model_id: str,
        duration: int = 10,
        resolution: str = "1080p",
        extended_params: dict[str, Any] | None = None,
    ) -> list[GenerationTask]:
        """Submit multiple tasks: one per tag for the same model"""
        tasks = []
        for tag_id in tag_ids:
            task = await self.submit(
                user_id=user_id,
                image_asset_id=image_asset_id,
                tag_id=tag_id,
                model_id=model_id,
                duration=duration,
                resolution=resolution,
                extended_params=extended_params,
            )
            tasks.append(task)
        return tasks

    async def update_task_status(self, task_id: str, status: str, video_url: str | None = None, error_message: str | None = None) -> None:
        """Update task status (called by ARQ polling worker)"""
        result = await self.db.execute(select(GenerationTask).where(GenerationTask.id == uuid.UUID(task_id)))
        task = result.scalar_one_or_none()
        if not task:
            return

        task.status = status
        if status == "completed":
            task.completed_at = datetime.now(timezone.utc)
            if video_url:
                # Download video from external URL and upload to MinIO
                try:
                    storage_url = await storage_service.download_video_from_url(video_url, task_id)
                    task.result_video_key = f"videos/{task_id}.mp4"
                except Exception:
                    pass
        elif status == "failed":
            task.completed_at = datetime.now(timezone.utc)
            task.error_message = error_message

        await self.db.flush()

    async def get_task(self, task_id: str) -> GenerationTask:
        result = await self.db.execute(select(GenerationTask).where(GenerationTask.id == uuid.UUID(task_id)))
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundError("任务不存在")
        return task

    async def rate_task(self, task_id: str, quality_score: int, quality_notes: str | None = None) -> GenerationTask:
        task = await self.get_task(task_id)
        task.quality_score = quality_score
        task.quality_notes = quality_notes
        await self.db.flush()
        return task

    # ── Private helpers ──

    async def _get_model(self, model_id: str) -> ModelConfig:
        result = await self.db.execute(select(ModelConfig).where(ModelConfig.id == uuid.UUID(model_id)))
        model = result.scalar_one_or_none()
        if not model:
            raise NotFoundError("模型不存在")
        return model

    async def _get_tag(self, tag_id: str) -> StyleTag:
        result = await self.db.execute(select(StyleTag).where(StyleTag.id == uuid.UUID(tag_id)))
        tag = result.scalar_one_or_none()
        if not tag:
            raise NotFoundError("标签不存在")
        return tag

    async def _get_image(self, image_id: str) -> ImageAsset:
        result = await self.db.execute(select(ImageAsset).where(ImageAsset.id == uuid.UUID(image_id)))
        img = result.scalar_one_or_none()
        if not img:
            raise NotFoundError("图片不存在")
        return img

    async def _find_or_create_group(self, user_uuid: uuid.UUID, image_id: str, tag_id: str, model_id: str) -> GenerationGroup:
        result = await self.db.execute(
            select(GenerationGroup).where(
                GenerationGroup.user_id == user_uuid,
                GenerationGroup.image_asset_id == uuid.UUID(image_id),
                GenerationGroup.tag_id == uuid.UUID(tag_id),
                GenerationGroup.model_id == uuid.UUID(model_id),
            )
        )
        group = result.scalar_one_or_none()
        if group:
            return group

        group = GenerationGroup(
            id=uuid.uuid4(),
            image_asset_id=uuid.UUID(image_id),
            tag_id=uuid.UUID(tag_id),
            model_id=uuid.UUID(model_id),
            user_id=user_uuid,
        )
        self.db.add(group)
        await self.db.flush()
        return group

    @staticmethod
    def _build_prompt(template: str, metadata: dict) -> str:
        """Replace {变量} placeholders with image metadata values"""
        prompt = template
        for key, val in metadata.items():
            prompt = prompt.replace(f"{{{key}}}", str(val) if val else "")
        # Remove remaining un-mapped variables
        import re
        prompt = re.sub(r"\{[^}]+\}", "", prompt)
        return prompt.strip()
