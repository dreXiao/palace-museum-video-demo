"""
适配器注册中心 — 根据模型配置的 api_type 创建对应适配器
"""
from app.adapters.base import BaseAdapter
from app.adapters.wan import WanAdapter
from app.adapters.seedance import SeedanceAdapter
from app.adapters.kling import KlingAdapter
from app.adapters.custom import CustomAdapter
from app.models.model_config import ModelConfig


ADAPTER_MAP: dict[str, type[BaseAdapter]] = {
    "dashscope": WanAdapter,
    "volcengine-ark": SeedanceAdapter,
    "kling": KlingAdapter,
    "custom": CustomAdapter,
}


class AdapterRegistry:
    """适配器工厂 — 根据配置创建对应的 API 适配器实例"""

    @staticmethod
    def create(config: ModelConfig) -> BaseAdapter:
        adapter_cls = ADAPTER_MAP.get(config.api_type, CustomAdapter)
        return adapter_cls(config)
