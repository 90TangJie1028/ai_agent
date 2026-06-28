"""ModelGateway：统一多模型调用入口。"""

from __future__ import annotations

import asyncio

from model_gateway.adapters.base import ChatAdapter
from model_gateway.adapters.deepseek import DeepSeekAdapter
from model_gateway.adapters.moonshot import MoonshotAdapter
from model_gateway.adapters.openai_compat import OpenAICompatAdapter
from model_gateway.adapters.openai_provider import OpenAIProviderAdapter
from model_gateway.config import (
    get_default_provider,
    get_gateway_max_concurrent,
    get_gateway_qps,
    get_gateway_rate_burst,
    load_providers,
)
from model_gateway.metrics import CallRecord, GatewayResult
from model_gateway.ratelimit import RateLimitConfig, TokenBucket


def _default_rate_limiter() -> TokenBucket:
    burst_env = get_gateway_rate_burst()
    burst = burst_env if burst_env > 0 else max(1, int(get_gateway_qps()))
    return TokenBucket.from_config(RateLimitConfig(rate=get_gateway_qps(), burst=burst))


class ModelGateway:
    def __init__(
        self,
        provider: str | None = None,
        *,
        rate_limiter: TokenBucket | None = None,
        max_concurrent: int | None = None,
    ) -> None:
        self._providers = load_providers()
        self._default_provider = provider or get_default_provider()
        self._adapters = self._build_adapters()
        self._rate_limiter = rate_limiter or _default_rate_limiter()
        self._concurrency = asyncio.Semaphore(
            max_concurrent if max_concurrent is not None else get_gateway_max_concurrent()
        )

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
        # * 表示此处以下参数必须作为关键字参数（必须加参数名传入，不能位置传参）
        # Python 3 的“仅关键字参数”标记，类似 TypeScript、Java、C++ 无强制命名参数，对应 Lua 使用 table 传名值对
        *,
        provider: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ) -> GatewayResult:
        name = (provider or self._default_provider).lower()
        if name not in self._adapters:
            configured = ", ".join(self.available_providers) or "无"
            raise ValueError(
                f"未配置 provider={name!r}。请在 .env 填入对应 API Key。"
                f" 当前可用: {configured}"
            )
        model_name = model or self._providers[name].default_model
        try:
            chat_result = self._adapters[name].chat(message, model=model_name, timeout=timeout)
        except Exception as e:
            record = CallRecord.from_error(provider=name, model=model_name, exc=e)
            return GatewayResult(result=None, record=record)
        record = CallRecord.from_chat_result(chat_result)
        return GatewayResult(result=chat_result, record=record)

    async def async_chat(
        self,
        message: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ) -> GatewayResult:
        """异步 chat：Semaphore 限并发，令牌桶限 QPS，同步 SDK 走 to_thread。"""
        async with self._concurrency:
            await self._rate_limiter.acquire()
            return await asyncio.to_thread(
                self.chat,
                message,
                provider=provider,
                model=model,
                timeout=timeout,
            )

    async def async_chat_batch(
        self,
        messages: list[str],
        *,
        provider: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ) -> list[GatewayResult]:
        """批量并发 chat；并发上限由 Gateway Semaphore 控制。"""
        tasks = [
            self.async_chat(
                msg,
                provider=provider,
                model=model,
                timeout=timeout,
            )
            for msg in messages
        ]
        return list(await asyncio.gather(*tasks))
