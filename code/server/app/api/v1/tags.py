"""
标签管理 API: /api/v1/tags/*
"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.style_tag import StyleTag, StyleTagVersion
from app.schemas.tag import TagCreate, TagUpdate, TagOut, TagVersionOut
from app.schemas.common import ApiResponse
from app.api.deps import get_current_user, get_admin_user
from app.core.exceptions import PresetDeleteError, NotFoundError
from app.models.user import User

router = APIRouter()


@router.get("", response_model=ApiResponse[list[TagOut]])
async def list_tags(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StyleTag).order_by(StyleTag.is_preset.desc(), StyleTag.usage_count.desc())
    )
    tags = result.scalars().all()
    return ApiResponse(
        success=True,
        data=[_tag_to_out(t) for t in tags],
    )


@router.post("", response_model=ApiResponse[TagOut])
async def create_tag(
    req: TagCreate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    tag = StyleTag(
        name=req.name,
        color=req.color,
        icon=req.icon,
        description=req.description,
        applicable_types=req.applicable_types,
        positive_prompt=req.positive_prompt,
        negative_prompt=req.negative_prompt,
        variables=req.variables,
        default_params=req.default_params,
        is_preset=False,
        created_by=current_user.id,
    )
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return ApiResponse(success=True, data=_tag_to_out(tag))


@router.put("/{tag_id}", response_model=ApiResponse[TagOut])
async def update_tag(
    tag_id: str,
    req: TagUpdate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(StyleTag).where(StyleTag.id == uuid.UUID(tag_id)))
    tag = result.scalar_one_or_none()
    if not tag:
        raise NotFoundError("标签不存在")

    # Save version snapshot before update
    version_count = await db.execute(
        select(StyleTagVersion).where(StyleTagVersion.tag_id == tag.id)
    )
    existing_versions = version_count.scalars().all()
    next_version = len(existing_versions) + 1

    snapshot = {
        "name": tag.name, "color": tag.color, "icon": tag.icon,
        "description": tag.description, "positive_prompt": tag.positive_prompt,
        "negative_prompt": tag.negative_prompt, "variables": tag.variables,
        "default_params": tag.default_params,
    }
    version = StyleTagVersion(
        tag_id=tag.id,
        version_number=next_version,
        snapshot=snapshot,
        change_note=req.change_note,
        created_by=current_user.id,
    )
    db.add(version)

    # Update fields
    update_data = req.model_dump(exclude_unset=True, exclude={"change_note"})
    for key, val in update_data.items():
        setattr(tag, key, val)

    await db.flush()
    await db.refresh(tag)
    return ApiResponse(success=True, data=_tag_to_out(tag))


@router.delete("/{tag_id}", response_model=ApiResponse[None])
async def delete_tag(
    tag_id: str,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(StyleTag).where(StyleTag.id == uuid.UUID(tag_id)))
    tag = result.scalar_one_or_none()
    if not tag:
        raise NotFoundError("标签不存在")
    if tag.is_preset:
        raise PresetDeleteError("标签")
    await db.delete(tag)
    return ApiResponse(success=True, message="已删除")


@router.post("/{tag_id}/copy", response_model=ApiResponse[TagOut])
async def copy_tag(
    tag_id: str,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(StyleTag).where(StyleTag.id == uuid.UUID(tag_id)))
    original = result.scalar_one_or_none()
    if not original:
        raise NotFoundError("标签不存在")
    copy = StyleTag(
        name=f"{original.name} (副本)",
        color=original.color,
        icon=original.icon,
        description=original.description,
        applicable_types=original.applicable_types,
        positive_prompt=original.positive_prompt,
        negative_prompt=original.negative_prompt,
        variables=original.variables,
        default_params=original.default_params,
        is_preset=False,
        created_by=current_user.id,
    )
    db.add(copy)
    await db.flush()
    await db.refresh(copy)
    return ApiResponse(success=True, data=_tag_to_out(copy))


@router.get("/{tag_id}/versions", response_model=ApiResponse[list[TagVersionOut]])
async def get_tag_versions(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StyleTagVersion)
        .where(StyleTagVersion.tag_id == uuid.UUID(tag_id))
        .order_by(desc(StyleTagVersion.version_number))
    )
    versions = result.scalars().all()
    return ApiResponse(
        success=True,
        data=[TagVersionOut(
            id=str(v.id), tag_id=str(v.tag_id),
            version_number=v.version_number, snapshot=v.snapshot,
            change_note=v.change_note, created_at=str(v.created_at),
        ) for v in versions],
    )


def _tag_to_out(tag: StyleTag) -> TagOut:
    return TagOut(
        id=str(tag.id),
        name=tag.name,
        color=tag.color,
        icon=tag.icon,
        description=tag.description,
        applicable_types=tag.applicable_types,
        positive_prompt=tag.positive_prompt,
        negative_prompt=tag.negative_prompt,
        variables=tag.variables,
        default_params=tag.default_params,
        is_preset=tag.is_preset,
        usage_count=tag.usage_count or 0,
        created_at=str(tag.created_at),
        updated_at=str(tag.updated_at),
    )
