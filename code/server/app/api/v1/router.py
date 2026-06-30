"""
v1 API 路由聚合
"""
from fastapi import APIRouter
from app.api.v1 import auth, generation, history, models, tags, media, settings

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router, prefix="/auth", tags=["认证"])
router.include_router(generation.router, prefix="/generation", tags=["生成任务"])
router.include_router(history.router, prefix="/history", tags=["生成历史"])
router.include_router(models.router, prefix="/models", tags=["模型管理"])
router.include_router(tags.router, prefix="/tags", tags=["标签管理"])
router.include_router(media.router, prefix="/media", tags=["媒体文件"])
router.include_router(settings.router, prefix="/settings", tags=["用户设置"])
