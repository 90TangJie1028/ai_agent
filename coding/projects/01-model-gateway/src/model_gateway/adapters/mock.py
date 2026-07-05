"""Mock 适配器：无需 API Key，用于本地开发与测试。"""

from __future__ import annotations

import json
import time
from typing import Any

from model_gateway.adapters.base import ChatResult


class MockAdapter:
    """返回确定性 echo 回复，不发起网络请求。"""

    provider = "mock"

    def chat(
        self,
        message: str,
        *,
        model: str | None = None,
        timeout: float | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> ChatResult:
        del timeout  # mock 忽略超时
        if not message.strip():
            raise ValueError("empty prompt")
        if message == "__bench_fail__":
            raise RuntimeError("simulated bench failure")
        started = time.perf_counter()
        model_name = model or "mock-model"
        if response_format is not None:
            content = json.dumps(
                {
                    "answer": f"[mock-json] {message[:80]}",
                    "confidence": 0.85,
                    "sources": ["mock"],
                },
                ensure_ascii=False,
            )
        else:
            content = f"[mock] echo: {message}"
        prompt_tokens = max(1, len(message) // 4)
        completion_tokens = max(1, len(content) // 4)
        latency_ms = max(1, int((time.perf_counter() - started) * 1000))
        return ChatResult(
            content=content,
            model=model_name,
            provider=self.provider,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=latency_ms,
        )
