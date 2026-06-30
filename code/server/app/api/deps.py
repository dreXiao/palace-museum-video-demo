"""
FastAPI 依赖注入
"""
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import decode_token
from app.models.user import User
from sqlalchemy import select

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 JWT token 获取当前用户"""
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """确保当前用户是管理员"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    return current_user


async def get_dev_user(current_user: User = Depends(get_current_user)) -> User:
    """确保当前用户是开发者或管理员"""
    if current_user.role not in ("admin", "developer"):
        raise HTTPException(status_code=403, detail="Developer or admin required")
    return current_user
