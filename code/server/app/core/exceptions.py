"""
自定义异常 + 全局异常处理器
"""
from fastapi import HTTPException


class AppError(HTTPException):
    """应用级异常，带 error_code"""

    def __init__(self, status_code: int, message: str, error_code: str = "APP_ERROR"):
        super().__init__(status_code=status_code, detail=message)
        self.error_code = error_code


class NotFoundError(AppError):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(404, message, "NOT_FOUND")


class ForbiddenError(AppError):
    def __init__(self, message: str = "无权限"):
        super().__init__(403, message, "FORBIDDEN")


class ConflictError(AppError):
    def __init__(self, message: str = "冲突"):
        super().__init__(409, message, "CONFLICT")


class ModelNotConnectedError(AppError):
    def __init__(self, model_name: str):
        super().__init__(400, f"模型 '{model_name}' 未连通，请先测试连接", "MODEL_NOT_CONNECTED")


class ModelApiKeyMissingError(AppError):
    def __init__(self, model_name: str, env_name: str):
        super().__init__(400, f"模型 '{model_name}' 的 API Key 未配置 (环境变量 {env_name})", "MODEL_API_KEY_MISSING")


class PresetDeleteError(AppError):
    def __init__(self, resource: str):
        super().__init__(400, f"预设{resource}不可删除", "PRESET_DELETE_FORBIDDEN")
