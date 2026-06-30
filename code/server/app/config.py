"""
应用配置管理 — 使用 pydantic-settings 从环境变量加载
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── 应用 ──
    APP_NAME: str = "故宫日历·图生视频管理平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production-use-random-64-chars"

    # ── 数据库 ──
    DATABASE_URL: str = "postgresql+asyncpg://palace:palace@localhost:5432/palace_museum"

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── JWT ──
    JWT_SECRET_KEY: str = "change-me-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── 初始管理员 ──
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"  # 首次启动后请修改

    # ── 对象存储 (MinIO / OSS) ──
    STORAGE_ENDPOINT: str = "http://localhost:9000"
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin"
    STORAGE_BUCKET: str = "palace-museum-media"
    STORAGE_USE_SSL: bool = False

    # ── AI API Keys ──
    DASHSCOPE_API_KEY: Optional[str] = None
    SEEDANCE_API_KEY: Optional[str] = None
    KLING_API_KEY: Optional[str] = None
    KLING_API_SECRET: Optional[str] = None

    # ── CORS ──
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── 速率限制 ──
    RATE_LIMIT_GENERATION: str = "10/minute"


settings = Settings()
