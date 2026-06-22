"""基于 OpenAI Python SDK 的通用 Chat Completions 适配器。"""

from __future__ import annotations

import time

from openai import OpenAI

from model_gateway.adapters.base import ChatResult
from model_gateway.config import ProviderConfig


class OpenAICompatAdapter:
    """DeepSeek / Kimi / 通义 / OpenAI 等兼容接口均可复用此实现。"""

    def __init__(self, config: ProviderConfig) -> None:
        self.provider = config.name
        self._config = config
        self._client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def chat(self, message: str, *, model: str | None = None) -> ChatResult:
        model_name = model or self._config.default_model
        started = time.perf_counter()

        response = self._client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": message}],
        )

        latency_ms = int((time.perf_counter() - started) * 1000)
        choice = response.choices[0].message
        usage = response.usage

        return ChatResult(
            content=choice.content or "",
            model=response.model or model_name,
            provider=self.provider,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            latency_ms=latency_ms,
        )
