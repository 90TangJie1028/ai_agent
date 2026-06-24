"""基于 OpenAI Python SDK 的通用 Chat Completions 适配器。"""

from __future__ import annotations

import time

from openai import APITimeoutError, OpenAI

from model_gateway.adapters.base import ChatResult
from model_gateway.config import ProviderConfig, get_gateway_timeout
from model_gateway.retry import RetryPolicy, backoff_delay, is_retryable


class OpenAICompatAdapter:
    """DeepSeek / Kimi / 通义 / OpenAI 等兼容接口均可复用此实现。"""

    def __init__(
        self,
        config: ProviderConfig,
        *,
        timeout: float | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self.provider = config.name
        self._config = config
        self._timeout = timeout if timeout is not None else get_gateway_timeout()
        self._retry_policy = retry_policy or RetryPolicy()
        self._client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def chat(
        self,
        message: str,
        *,
        model: str | None = None,
        timeout: float | None = None,
    ) -> ChatResult:
        model_name = model or self._config.default_model
        effective_timeout = timeout if timeout is not None else self._timeout
        started = time.perf_counter()

        response = self._create_completion(
            model_name,
            message,
            timeout=effective_timeout,
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

    def _create_completion(self, model_name: str, message: str, *, timeout: float) -> object:
        policy = self._retry_policy
        last_exc: BaseException | None = None
        for attempt in range(policy.max_retries + 1):
            try:
                return self._client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": message}],
                    timeout=timeout,
                )
            except APITimeoutError as exc:
                raise TimeoutError(str(exc)) from exc
            except Exception as exc:
                if not is_retryable(exc) or attempt >= policy.max_retries:
                    raise
                last_exc = exc
                time.sleep(backoff_delay(attempt, policy))
        assert last_exc is not None
        raise last_exc
