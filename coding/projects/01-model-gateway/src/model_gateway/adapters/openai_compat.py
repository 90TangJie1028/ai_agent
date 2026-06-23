"""基于 OpenAI Python SDK 的通用 Chat Completions 适配器。"""

from __future__ import annotations

import time

from openai import OpenAI

from model_gateway.adapters.base import ChatResult
from model_gateway.config import ProviderConfig


class OpenAICompatAdapter:
    """DeepSeek / Kimi / 通义 / OpenAI 等兼容接口均可复用此实现。"""

    def __init__(self, config: ProviderConfig) -> None:
        # 根据传入的模型供应商配置，赋值 provider 属性和 _config 配置对象
        self.provider = config.name
        self._config = config
        # 用 openai-python SDK 初始化私有变量 _client
        self._client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def chat(self, message: str, *, model: str | None = None) -> ChatResult:
        model_name = model or self._config.default_model
        started = time.perf_counter()

        response = self._client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": message}],
        )

        latency_ms = int((time.perf_counter() - started) * 1000)
        # 从 response 对象中获取选择（choice）和使用情况（usage）
        # 选择（choice）是 response 对象的第一个选择（通常是第一个模型回复）
        choice = response.choices[0].message
        # 使用情况（usage）是 response 对象的用量信息，包含 prompt 和 completion 的 token 数
        usage = response.usage

        # 返回 ChatResult 对象，封装了模型回复内容、模型名、厂商名、Token 用量、延迟等信息
        return ChatResult(
            content=choice.content or "",
            model=response.model or model_name,
            provider=self.provider,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            latency_ms=latency_ms,
        )
