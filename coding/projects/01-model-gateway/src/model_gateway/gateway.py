"""ModelGateway：统一多模型调用入口。"""

from __future__ import annotations

import asyncio
from json import JSONDecodeError
from typing import Any

from model_gateway.adapters.base import ChatAdapter
from model_gateway.adapters.deepseek import DeepSeekAdapter
from model_gateway.adapters.mock import MockAdapter
from model_gateway.adapters.moonshot import MoonshotAdapter
from model_gateway.adapters.openai_compat import OpenAICompatAdapter
from model_gateway.adapters.openai_provider import OpenAIProviderAdapter
from model_gateway.config import (
    ProviderConfig,
    get_default_provider,
    get_gateway_max_concurrent,
    get_gateway_qps,
    get_gateway_rate_burst,
    load_providers,
)
from pydantic import ValidationError

from model_gateway.adapters.base import ChatResult
from model_gateway.metrics import CallRecord, GatewayResult, compute_cost_usd
from model_gateway.ratelimit import RateLimitConfig, TokenBucket
from model_gateway.schemas import ChatRequest, StructuredAnswer
from model_gateway.structured_output import (
    StructuredOutputMode,
    build_response_format,
    build_structured_prompt,
    parse_structured_response,
)
from model_gateway.tools.calculator import build_default_registry
from model_gateway.tools.registry import ToolRegistry


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
        self._ensure_mock_provider()
        self._default_provider = provider or get_default_provider()
        self._adapters = self._build_adapters()
        self._rate_limiter = rate_limiter or _default_rate_limiter()
        self._concurrency = asyncio.Semaphore(
            max_concurrent if max_concurrent is not None else get_gateway_max_concurrent()
        )

    def _ensure_mock_provider(self) -> None:
        """mock 厂商无需 API Key，始终可用于本地测试。"""
        if "mock" not in self._providers:
            self._providers["mock"] = ProviderConfig(
                name="mock",
                api_key="mock",
                base_url="mock://local",
                default_model="mock-model",
            )

    def _build_adapters(self) -> dict[str, ChatAdapter]:
        mapping: dict[str, type[OpenAICompatAdapter]] = {
            "deepseek": DeepSeekAdapter,
            "moonshot": MoonshotAdapter,
            "openai": OpenAIProviderAdapter,
        }
        adapters: dict[str, ChatAdapter] = {"mock": MockAdapter()}
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
        response_format: dict[str, Any] | None = None,
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
            chat_result = self._adapters[name].chat(
                message,
                model=model_name,
                timeout=timeout,
                response_format=response_format,
            )
        except Exception as e:
            record = CallRecord.from_error(provider=name, model=model_name, exc=e)
            return GatewayResult(result=None, record=record)
        record = CallRecord.from_chat_result(chat_result)
        return GatewayResult(result=chat_result, record=record)

    def chat_structured(
        self,
        message: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        response_model: type[StructuredAnswer] = StructuredAnswer,
        mode: StructuredOutputMode = "prompt",
    ) -> GatewayResult:
        """结构化输出：按 mode 拼 prompt / response_format → chat → parse → 校验。"""
        name = (provider or self._default_provider).lower()
        if name in self._providers:
            model_name = model or self._providers[name].default_model
        else:
            model_name = model or "unknown"
        try:
            req = ChatRequest(message=message, provider=provider, model=model)
        except ValidationError as e:
            record = CallRecord.from_error(provider=name, model=model_name, exc=e)
            return GatewayResult(result=None, record=record)

        prompt = build_structured_prompt(req.message, mode, response_model)
        response_format = build_response_format(mode, response_model)

        gw = self.chat(
            prompt,
            provider=req.provider,
            model=req.model,
            timeout=timeout,
            response_format=response_format,
        )
        if gw.result is None:
            return gw

        name = (req.provider or self._default_provider).lower()
        model_name = model or self._providers[name].default_model
        try:
            answer = parse_structured_response(gw.result.content, response_model)
        except (JSONDecodeError, ValidationError) as e:
            record = CallRecord.from_error(provider=name, model=model_name, exc=e)
            return GatewayResult(result=None, record=record)

        gw.result.content = answer.model_dump_json()
        return gw

    def chat_with_tools(
        self,
        message: str,
        *,
        registry: ToolRegistry | None = None,
        provider: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        max_tool_rounds: int = 1,
    ) -> GatewayResult:
        """Function Calling 闭环：带 tools → 本地执行 → 回灌 → 最终答案。

        类似 Cursor Agent：模型只声明调哪个工具；真正执行在本地（Registry handler）。
        D11 默认最多 1 轮工具调用（够 calculator E2E）。
        """
        name = (provider or self._default_provider).lower()
        if name not in self._adapters:
            configured = ", ".join(self.available_providers) or "无"
            raise ValueError(
                f"未配置 provider={name!r}。请在 .env 填入对应 API Key。"
                f" 当前可用: {configured}"
            )
        model_name = model or self._providers[name].default_model
        reg = registry or build_default_registry()
        tools = reg.to_openai_tools()
        messages: list[dict[str, Any]] = [{"role": "user", "content": message}]
        adapter = self._adapters[name]
        rounds: list[ChatResult] = []

        try:
            for _ in range(max_tool_rounds + 1):
                chat_result = adapter.chat_messages(
                    messages,
                    model=model_name,
                    timeout=timeout,
                    tools=tools,
                )
                rounds.append(chat_result)

                if not chat_result.tool_calls:
                    return GatewayResult(
                        result=chat_result,
                        record=_record_from_rounds(rounds),
                    )

                if len(rounds) > max_tool_rounds:
                    # 仍要调工具但轮次用尽：返回当前结果（通常 content 为空）
                    return GatewayResult(
                        result=chat_result,
                        record=_record_from_rounds(rounds),
                    )

                messages.append(chat_result.to_assistant_message())
                for tc in chat_result.tool_calls:
                    try:
                        tool_out = reg.call(tc.name, tc.arguments)
                        tool_content = str(tool_out)
                    except Exception as exc:  # ValidationError / 未知工具 / 求值失败
                        tool_content = f"error: {type(exc).__name__}: {exc}"
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": tool_content,
                        }
                    )
        except Exception as e:
            record = CallRecord.from_error(provider=name, model=model_name, exc=e)
            return GatewayResult(result=None, record=record)

        # 理论上不会走到这里
        last = rounds[-1] if rounds else None
        if last is None:
            record = CallRecord.from_error(
                provider=name,
                model=model_name,
                exc=RuntimeError("chat_with_tools produced no rounds"),
            )
            return GatewayResult(result=None, record=record)
        return GatewayResult(result=last, record=_record_from_rounds(rounds))

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


def _record_from_rounds(rounds: list[ChatResult]) -> CallRecord:
    """把多轮 API 调用的 token / 延迟累加进一条 CallRecord。"""
    last = rounds[-1]
    prompt = sum(r.prompt_tokens for r in rounds)
    completion = sum(r.completion_tokens for r in rounds)
    total = sum(r.total_tokens for r in rounds)
    latency = sum(r.latency_ms for r in rounds)
    return CallRecord(
        provider=last.provider,
        model=last.model,
        prompt_tokens=prompt,
        completion_tokens=completion,
        total_tokens=total,
        latency_ms=latency,
        cost_usd=compute_cost_usd(last.model, prompt, completion),
        success=True,
    )

