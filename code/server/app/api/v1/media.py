"""
媒体文件 API: /api/v1/media/*
"""
import uuid
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.image_asset import ImageAsset
from app.schemas.common import ApiResponse
from app.api.deps import get_current_user
from app.core.storage import storage_service
from app.models.user import User
from PIL import Image
import io

router = APIRouter()


@router.post("/upload", response_model=ApiResponse[dict])
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传古画图片"""
    if file.content_type not in ("image/png", "image/jpeg", "image/webp"):
        return ApiResponse(success=False, message="仅支持 PNG/JPG/WEBP 格式")

    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        return ApiResponse(success=False, message="文件大小不能超过 20MB")

    # Get image dimensions
    img = Image.open(io.BytesIO(content))
    width, height = img.size
    mime = file.content_type or "image/png"

    # Upload to storage
    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "png"
    storage_key = f"images/{uuid.uuid4().hex}.{ext}"
    storage_url = await storage_service.upload_bytes(content, storage_key, mime)

    # Create database record
    asset = ImageAsset(
        original_name=file.filename or "unnamed",
        storage_key=storage_key,
        storage_url=storage_url,
        width=width,
        height=height,
        size_bytes=len(content),
        mime_type=mime,
        metadata={
            "category": "",
            "dynasty": "",
            "artist": "",
            "material": "",
        },
        created_by=current_user.id,
    )
    db.add(asset)
    await db.flush()
    await db.refresh(asset)

    return ApiResponse(
        success=True,
        data={
            "id": str(asset.id),
            "original_name": asset.original_name,
            "width": asset.width,
            "height": asset.height,
            "size_bytes": asset.size_bytes,
            "mime_type": asset.mime_type,
            "storage_url": storage_url,
            "metadata": asset.metadata,
        },
    )


@router.get("/image/{asset_id}", response_model=ApiResponse[dict])
async def get_image(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ImageAsset).where(ImageAsset.id == uuid.UUID(asset_id)))
    asset = result.scalar_one_or_none()
    if not asset:
        return ApiResponse(success=False, message="图片不存在")
    presigned_url = storage_service.get_presigned_url(asset.storage_key)
    return ApiResponse(
        success=True,
        data={
            "id": str(asset.id),
            "original_name": asset.original_name,
            "width": asset.width,
            "height": asset.height,
            "url": presigned_url,
            "metadata": asset.metadata,
        },
    )
