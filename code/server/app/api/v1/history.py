"""
生成历史 API: /api/v1/history/*
"""
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.generation_group import GenerationGroup
from app.models.generation_task import GenerationTask
from app.schemas.generation import GenerationGroupOut, GenerationTaskOut
from app.schemas.common import ApiResponse, PaginationMeta
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/groups", response_model=ApiResponse[list[GenerationGroupOut]])
async def list_groups(
    model: str | None = Query(None, alias="model"),
    tag: str | None = Query(None, alias="tag"),
    status: str | None = Query(None),
    rating: int | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分页查询生成分组"""
    query = select(GenerationGroup).where(GenerationGroup.user_id == current_user.id)
    if cursor:
        query = query.where(GenerationGroup.created_at < cursor)
    query = query.order_by(desc(GenerationGroup.created_at)).limit(limit + 1)

    result = await db.execute(query)
    groups = result.scalars().all()

    has_more = len(groups) > limit
    items = groups[:limit]
    next_cursor = str(items[-1].created_at) if has_more and items else None

    return ApiResponse(
        success=True,
        data=[GenerationGroupOut(
            id=str(g.id), image_asset_id=str(g.image_asset_id),
            tag_id=str(g.tag_id), model_id=str(g.model_id),
            user_id=str(g.user_id), best_attempt_id=str(g.best_attempt_id) if g.best_attempt_id else None,
            total_attempts=g.total_attempts, total_cost_yuan=g.total_cost_yuan,
            created_at=str(g.created_at), updated_at=str(g.updated_at),
        ) for g in items],
        pagination=PaginationMeta(cursor=next_cursor, has_more=has_more, total=0),
    )


@router.get("/groups/{group_id}", response_model=ApiResponse[dict])
async def get_group_detail(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分组详情 + 所有尝试"""
    result = await db.execute(select(GenerationGroup).where(GenerationGroup.id == uuid.UUID(group_id)))
    group = result.scalar_one_or_none()
    if not group:
        return ApiResponse(success=False, message="分组不存在")

    tasks_result = await db.execute(
        select(GenerationTask)
        .where(GenerationTask.group_id == uuid.UUID(group_id))
        .order_by(GenerationTask.attempt_number)
    )
    tasks = tasks_result.scalars().all()

    return ApiResponse(
        success=True,
        data={
            "group": GenerationGroupOut(
                id=str(group.id), image_asset_id=str(group.image_asset_id),
                tag_id=str(group.tag_id), model_id=str(group.model_id),
                user_id=str(group.user_id),
                best_attempt_id=str(group.best_attempt_id) if group.best_attempt_id else None,
                total_attempts=group.total_attempts, total_cost_yuan=group.total_cost_yuan,
                created_at=str(group.created_at), updated_at=str(group.updated_at),
            ),
            "attempts": [
                GenerationTaskOut(
                    id=str(t.id), group_id=str(t.group_id), user_id=str(t.user_id),
                    image_asset_id=str(t.image_asset_id), tag_snapshot=t.tag_snapshot,
                    model_snapshot=t.model_snapshot, prompt=t.prompt,
                    negative_prompt=t.negative_prompt, duration=t.duration,
                    resolution=t.resolution, status=t.status,
                    result_video_url=t.result_video_key,
                    result_thumbnail_url=t.result_thumbnail_key,
                    error_message=t.error_message,
                    quality_score=t.quality_score, quality_notes=t.quality_notes,
                    is_best_attempt=t.is_best_attempt, attempt_number=t.attempt_number,
                    generation_time_seconds=t.generation_time_seconds,
                    cost_yuan=t.cost_yuan,
                    created_at=str(t.created_at) if t.created_at else "",
                    completed_at=str(t.completed_at) if t.completed_at else None,
                )
                for t in tasks
            ],
        },
    )


@router.delete("/groups/{group_id}", response_model=ApiResponse[None])
async def delete_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(GenerationGroup).where(
        GenerationGroup.id == uuid.UUID(group_id),
        GenerationGroup.user_id == current_user.id,
    ))
    group = result.scalar_one_or_none()
    if not group:
        return ApiResponse(success=False, message="分组不存在")
    await db.delete(group)
    return ApiResponse(success=True, message="已删除")
