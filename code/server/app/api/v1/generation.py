"""
生成任务 API: /api/v1/generation/*
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.generation import GenerationSubmitRequest, BatchSubmitRequest, TaskRateRequest, GenerationTaskOut
from app.schemas.common import ApiResponse
from app.services.generation import GenerationService
from app.api.deps import get_current_user, get_dev_user
from app.models.user import User

router = APIRouter()


@router.post("/submit", response_model=ApiResponse[GenerationTaskOut])
async def submit_generation(
    req: GenerationSubmitRequest,
    current_user: User = Depends(get_dev_user),
    db: AsyncSession = Depends(get_db),
):
    service = GenerationService(db)
    task = await service.submit(
        user_id=str(current_user.id),
        image_asset_id=req.image_asset_id,
        tag_id=req.tag_ids[0],
        model_id=req.model_id,
        duration=req.duration,
        resolution=req.resolution,
        extended_params=req.extended_params,
    )
    return ApiResponse(success=True, data=_task_to_out(task))


@router.post("/batch-submit", response_model=ApiResponse[list[GenerationTaskOut]])
async def batch_submit(
    req: BatchSubmitRequest,
    current_user: User = Depends(get_dev_user),
    db: AsyncSession = Depends(get_db),
):
    service = GenerationService(db)
    tasks = []
    for tag_id in req.tag_ids:
        for model_id in req.model_ids:
            task = await service.submit(
                user_id=str(current_user.id),
                image_asset_id=req.image_asset_id,
                tag_id=tag_id,
                model_id=model_id,
                duration=req.duration,
                resolution=req.resolution,
                extended_params=req.extended_params,
            )
            tasks.append(task)
    return ApiResponse(success=True, data=[_task_to_out(t) for t in tasks])


@router.get("/{task_id}/status", response_model=ApiResponse[GenerationTaskOut])
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = GenerationService(db)
    task = await service.get_task(task_id)
    return ApiResponse(success=True, data=_task_to_out(task))


@router.post("/{task_id}/rate", response_model=ApiResponse[GenerationTaskOut])
async def rate_task(
    task_id: str,
    req: TaskRateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = GenerationService(db)
    task = await service.rate_task(task_id, req.quality_score, req.quality_notes)
    return ApiResponse(success=True, data=_task_to_out(task))


def _task_to_out(task) -> GenerationTaskOut:
    return GenerationTaskOut(
        id=str(task.id),
        group_id=str(task.group_id),
        user_id=str(task.user_id),
        image_asset_id=str(task.image_asset_id),
        tag_snapshot=task.tag_snapshot,
        model_snapshot=task.model_snapshot,
        prompt=task.prompt,
        negative_prompt=task.negative_prompt,
        duration=task.duration,
        resolution=task.resolution,
        status=task.status,
        result_video_url=task.result_video_key,
        result_thumbnail_url=task.result_thumbnail_key,
        error_message=task.error_message,
        quality_score=task.quality_score,
        quality_notes=task.quality_notes,
        is_best_attempt=task.is_best_attempt,
        attempt_number=task.attempt_number,
        generation_time_seconds=task.generation_time_seconds,
        cost_yuan=task.cost_yuan,
        created_at=str(task.created_at) if task.created_at else "",
        completed_at=str(task.completed_at) if task.completed_at else None,
    )
