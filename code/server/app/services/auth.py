"""
认证服务 — 登录 / 注册 / Token
"""
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.config import settings


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, username: str, password: str) -> dict | None:
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.password_hash):
            return None
        token_data = {"sub": str(user.id), "username": user.username, "role": user.role}
        return {
            "access_token": create_access_token(token_data),
            "refresh_token": create_refresh_token(token_data),
            "user": {"id": str(user.id), "username": user.username, "role": user.role, "is_active": user.is_active},
        }

    async def refresh_token(self, refresh_token: str) -> dict | None:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                return None
            user_id = payload.get("sub")
            result = await self.db.execute(select(User).where(User.id == uuid.UUID(user_id)))
            user = result.scalar_one_or_none()
            if not user or not user.is_active:
                return None
            token_data = {"sub": str(user.id), "username": user.username, "role": user.role}
            return {"access_token": create_access_token(token_data)}
        except Exception:
            return None

    async def get_user(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def ensure_admin_exists(self) -> None:
        """Ensure the initial admin user exists"""
        result = await self.db.execute(select(User).where(User.username == settings.ADMIN_USERNAME))
        if not result.scalar_one_or_none():
            admin = User(
                username=settings.ADMIN_USERNAME,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                role="admin",
            )
            self.db.add(admin)
            await self.db.flush()
