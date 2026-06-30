"""
认证 API: /api/v1/auth/*
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, UserInfo
from app.schemas.common import ApiResponse
from app.services.auth import AuthService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    auth = AuthService(db)
    result = await auth.login(req.username, req.password)
    if not result:
        return ApiResponse(success=False, message="用户名或密码错误")
    return ApiResponse(
        success=True,
        data=TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
        ),
    )


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    auth = AuthService(db)
    result = await auth.refresh_token(req.refresh_token)
    if not result:
        return ApiResponse(success=False, message="Invalid refresh token")
    return ApiResponse(
        success=True,
        data=TokenResponse(access_token=result["access_token"], refresh_token=req.refresh_token),
    )


@router.get("/me", response_model=ApiResponse[UserInfo])
async def me(current_user: User = Depends(get_current_user)):
    return ApiResponse(
        success=True,
        data=UserInfo(
            id=str(current_user.id),
            username=current_user.username,
            role=current_user.role,
            is_active=current_user.is_active,
        ),
    )
