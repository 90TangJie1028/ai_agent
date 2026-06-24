"""ModelGateway：统一多模型调用入口。"""

# "from __future__ import annotations" 的作用是允许在 Python 代码中，
# 类型注解可以用字符串表示自己定义类型，即使类型在文件中是稍后才定义的。
# 这主要用于提升类型注解的兼容性和解决前向引用问题。
# 对于 Python 3.7 及以上版本推荐使用，可减少循环依赖和提升编辑器类型提示体验。
from __future__ import annotations

from model_gateway.adapters.base import ChatAdapter, ChatResult
from model_gateway.adapters.deepseek import DeepSeekAdapter
from model_gateway.adapters.moonshot import MoonshotAdapter
from model_gateway.adapters.openai_compat import OpenAICompatAdapter
from model_gateway.adapters.openai_provider import OpenAIProviderAdapter
from model_gateway.config import get_default_provider, load_providers


class ModelGateway:
    def __init__(self, provider: str | None = None) -> None:
        self._providers = load_providers()
        self._default_provider = provider or get_default_provider()
        self._adapters = self._build_adapters()

    def _build_adapters(self) -> dict[str, ChatAdapter]:
        mapping: dict[str, type[OpenAICompatAdapter]] = {
            "deepseek": DeepSeekAdapter,
            "moonshot": MoonshotAdapter,
            "openai": OpenAIProviderAdapter,
        }
        adapters: dict[str, ChatAdapter] = {}
        for name, cls in mapping.items():
            if name in self._providers:
                adapters[name] = cls(self._providers[name])
        if "dashscope" in self._providers and "dashscope" not in adapters:
            adapters["dashscope"] = OpenAICompatAdapter(self._providers["dashscope"])
        return adapters

    @property
    def available_providers(self) -> list[str]:
        return sorted(self._adapters.keys())

    def chat(
        self,
        message: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ) -> ChatResult:
        name = (provider or self._default_provider).lower()
        if name not in self._adapters:
            configured = ", ".join(self.available_providers) or "无"
            raise ValueError(
                f"未配置 provider={name!r}。请在 .env 填入对应 API Key。"
                f" 当前可用: {configured}"
            )
        model_name = model or self._providers[name].default_model
        return self._adapters[name].chat(message, model=model_name, timeout=timeout)
