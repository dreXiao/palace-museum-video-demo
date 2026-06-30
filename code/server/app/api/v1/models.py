"""
模型管理 API: /api/v1/models/*
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.model_config import ModelConfig
from app.schemas.model_config import ModelConfigCreate, ModelConfigUpdate, ModelConfigOut
from app.schemas.common import ApiResponse
from app.api.deps import get_current_user, get_admin_user
from app.adapters.registry import AdapterRegistry
from app.core.exceptions import PresetDeleteError, NotFoundError
from app.models.user import User

router = APIRouter()


@router.get("", response_model=ApiResponse[list[ModelConfigOut]])
async def list_models(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ModelConfig).order_by(ModelConfig.is_default.desc()))
    models = result.scalars().all()
    return ApiResponse(success=True, data=[_model_to_out(m) for m in models])


@router.post("", response_model=ApiResponse[ModelConfigOut])
async def create_model(
    req: ModelConfigCreate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    model = ModelConfig(
        name=req.name,
        provider=req.provider,
        description=req.description,
        api_type=req.api_type,
        endpoint=req.endpoint,
        api_key_env=req.api_key_env,
        model_ids=req.model_ids,
        parameters=req.parameters,
        pricing=req.pricing,
        generation_config=req.generation_config,
        is_preset=False,
        created_by=current_user.id,
    )
    db.add(model)
    await db.flush()
    await db.refresh(model)
    return ApiResponse(success=True, data=_model_to_out(model))


@router.put("/{model_id}", response_model=ApiResponse[ModelConfigOut])
async def update_model(
    model_id: str,
    req: ModelConfigUpdate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ModelConfig).where(ModelConfig.id == uuid.UUID(model_id)))
    model = result.scalar_one_or_none()
    if not model:
        raise NotFoundError("模型不存在")

    update_data = req.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(model, key, val)

    await db.flush()
    await db.refresh(model)
    return ApiResponse(success=True, data=_model_to_out(model))


@router.delete("/{model_id}", response_model=ApiResponse[None])
async def delete_model(
    model_id: str,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ModelConfig).where(ModelConfig.id == uuid.UUID(model_id)))
    model = result.scalar_one_or_none()
    if not model:
        raise NotFoundError("模型不存在")
    if model.is_preset:
        raise PresetDeleteError("模型")
    await db.delete(model)
    return ApiResponse(success=True, message="已删除")


@router.post("/{model_id}/test", response_model=ApiResponse[dict])
async def test_model_connection(
    model_id: str,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ModelConfig).where(ModelConfig.id == uuid.UUID(model_id)))
    model = result.scalar_one_or_none()
    if not model:
        raise NotFoundError("模型不存在")

    adapter = AdapterRegistry.create(model)
    success, message = await adapter.test_connection()

    model.connection_status = "connected" if success else "failed"
    model.last_tested_at = datetime.now(timezone.utc)
    await db.flush()

    return ApiResponse(success=True, data={"status": model.connection_status, "message": message})


@router.post("/{model_id}/set-default", response_model=ApiResponse[None])
async def set_default_model(
    model_id: str,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(select(ModelConfig).where(ModelConfig.is_default == True))  # warm up
    all_models = (await db.execute(select(ModelConfig))).scalars().all()
    for m in all_models:
        m.is_default = False
    for m in all_models:
        if str(m.id) == model_id:
            m.is_default = True
    await db.flush()
    return ApiResponse(success=True, message="已设为默认模型")


def _model_to_out(m: ModelConfig) -> ModelConfigOut:
    return ModelConfigOut(
        id=str(m.id),
        name=m.name,
        provider=m.provider,
        description=m.description,
        api_type=m.api_type,
        endpoint=m.endpoint,
        api_key_env=m.api_key_env,
        model_ids=m.model_ids or {},
        parameters=m.parameters or {},
        pricing=m.pricing or {},
        generation_config=m.generation_config or {},
        is_default=m.is_default or False,
        is_preset=m.is_preset or False,
        connection_status=m.connection_status or "untested",
        last_tested_at=str(m.last_tested_at) if m.last_tested_at else None,
        created_at=str(m.created_at),
        updated_at=str(m.updated_at),
    )
