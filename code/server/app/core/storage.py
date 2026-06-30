"""
S3 兼容对象存储抽象 (MinIO / 阿里云 OSS)
"""
import uuid
from typing import BinaryIO
import httpx
from app.config import settings


class StorageService:
    """S3 兼容存储服务 — 当前使用 HTTP 直传 MinIO"""

    def __init__(self):
        self.endpoint = settings.STORAGE_ENDPOINT.rstrip("/")
        self.bucket = settings.STORAGE_BUCKET
        self.access_key = settings.STORAGE_ACCESS_KEY
        self.secret_key = settings.STORAGE_SECRET_KEY
        self.use_ssl = settings.STORAGE_USE_SSL

    def _public_url(self, key: str) -> str:
        scheme = "https" if self.use_ssl else "http"
        host = self.endpoint.split("://")[-1] if "://" in self.endpoint else self.endpoint
        return f"{scheme}://{host}/{self.bucket}/{key}"

    async def upload_bytes(self, data: bytes, key: str, content_type: str = "application/octet-stream") -> str:
        """上传字节数据到对象存储，返回公开访问 URL"""
        import hashlib, hmac, datetime as dt
        from email.utils import formatdate

        url = f"{self.endpoint}/{self.bucket}/{key}"
        date = formatdate(usegmt=True)
        signature = hmac.new(
            self.secret_key.encode(), f"PUT\n\n{content_type}\n{date}\n/{self.bucket}/{key}".encode(), hashlib.sha1
        ).digest().hex()

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.put(
                url,
                content=data,
                headers={
                    "Content-Type": content_type,
                    "Date": date,
                    "Authorization": f"AWS {self.access_key}:{signature}",
                },
            )
            resp.raise_for_status()
        return self._public_url(key)

    async def upload_file(self, file: BinaryIO, filename: str, content_type: str) -> str:
        """上传文件对象"""
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
        key = f"images/{uuid.uuid4().hex}.{ext}"
        content = file.read()
        return await self.upload_bytes(content, key, content_type)

    async def download_video_from_url(self, source_url: str, task_id: str) -> str:
        """从外部 API URL 下载视频并上传到对象存储"""
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.get(source_url)
            resp.raise_for_status()
            ext = "mp4"
            key = f"videos/{task_id}.{ext}"
            content_type = resp.headers.get("content-type", "video/mp4")
            return await self.upload_bytes(resp.content, key, content_type)

    def get_presigned_url(self, key: str, expires: int = 3600) -> str:
        """生成预签名下载 URL — 简化版，直接返回公开 URL"""
        return self._public_url(key)

    async def delete(self, key: str) -> None:
        """删除对象"""
        url = f"{self.endpoint}/{self.bucket}/{key}"
        async with httpx.AsyncClient(timeout=10) as client:
            await client.delete(url)


# 全局单例
storage_service = StorageService()
