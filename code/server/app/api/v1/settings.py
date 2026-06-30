"""
用户设置 API: /api/v1/settings/*
"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user_preference import UserPreference
from app.schemas.common import ApiResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/preferences", response_model=ApiResponse[dict])
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    pref = result.scalar_one_or_none()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)
        await db.flush()

    return ApiResponse(
        success=True,
        data={
            "default_resolution": pref.default_resolution,
            "default_duration": pref.default_duration,
            "history_view": pref.history_view,
            "page_size": pref.page_size,
            "language": pref.language,
            "theme": pref.theme,
        },
    )


@router.put("/preferences", response_model=ApiResponse[dict])
async def update_preferences(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    pref = result.scalar_one_or_none()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)

    allowed = {"default_resolution", "default_duration", "history_view", "page_size", "language", "theme"}
    for key, val in body.items():
        if key in allowed:
            setattr(pref, key, val)

    await db.flush()
    return ApiResponse(success=True, message="已保存")
