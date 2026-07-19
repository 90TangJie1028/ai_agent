"""基于 OpenAI Python SDK 的通用 Chat Completions 适配器。"""

from __future__ import annotations

import time
from typing import Any

from openai import APITimeoutError, OpenAI

from model_gateway.adapters.base import ChatResult, ToolCall
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
        response_format: dict[str, Any] | None = None,
    ) -> ChatResult:
        return self.chat_messages(
            [{"role": "user", "content": message}],
            model=model,
            timeout=timeout,
            response_format=response_format,
        )

    def chat_messages(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        timeout: float | None = None,
        tools: list[dict[str, Any]] | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> ChatResult:
        model_name = model or self._config.default_model
        started = time.perf_counter()
        effective_timeout = timeout if timeout is not None else self._timeout

        response = self._create_completion(
            model_name,
            messages,
            timeout=effective_timeout,
            tools=tools,
            response_format=response_format,
        )

        latency_ms = int((time.perf_counter() - started) * 1000)
        choice = response.choices[0]
        message = choice.message
        usage = response.usage
        tool_calls = _parse_tool_calls(message)

        return ChatResult(
            content=message.content or "",
            model=response.model or model_name,
            provider=self.provider,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            latency_ms=latency_ms,
            tool_calls=tool_calls,
            finish_reason=getattr(choice, "finish_reason", None),
        )

    def _create_completion(
        self,
        model_name: str,
        messages: list[dict[str, Any]],
        *,
        timeout: float,
        tools: list[dict[str, Any]] | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> Any:
        policy = self._retry_policy
        last_exc: BaseException | None = None
        for attempt in range(policy.max_retries + 1):
            try:
                kwargs: dict[str, Any] = {
                    "model": model_name,
                    "messages": messages,
                    "timeout": timeout,
                }
                if tools is not None:
                    kwargs["tools"] = tools
                if response_format is not None:
                    kwargs["response_format"] = response_format
                return self._client.chat.completions.create(**kwargs)
            except APITimeoutError as exc:
                raise TimeoutError(str(exc)) from exc
            except Exception as exc:
                if not is_retryable(exc) or attempt >= policy.max_retries:
                    raise
                last_exc = exc
                time.sleep(backoff_delay(attempt, policy))
        assert last_exc is not None
        raise last_exc


def _parse_tool_calls(message: Any) -> list[ToolCall]:
    raw = getattr(message, "tool_calls", None) or ()
    out: list[ToolCall] = []
    for item in raw:
        fn = getattr(item, "function", None)
        if fn is None:
            continue
        out.append(
            ToolCall(
                id=str(getattr(item, "id", "") or ""),
                name=str(getattr(fn, "name", "") or ""),
                arguments=str(getattr(fn, "arguments", None) or "{}"),
            )
        )
    return out
