"""Mock 适配器：无需 API Key，用于本地开发与测试。"""

from __future__ import annotations

import json
import re
import time
from typing import Any

from model_gateway.adapters.base import ChatResult, ToolCall

# 从用户话里抠一段像算式的子串，供模拟 tool_calls
_EXPR_RE = re.compile(r"[\d]+(?:\s*[+\-*/%()]+\s*[\d]+)+")


class MockAdapter:
    """返回确定性 echo / 模拟 calculator Function Calling，不发起网络请求。"""

    provider = "mock"

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
        del timeout
        if not messages:
            raise ValueError("empty messages")

        started = time.perf_counter()
        model_name = model or "mock-model"
        tool_names = _tool_names(tools)

        # 第 2 轮：已有 tool 结果 → 拼最终自然语言答案
        tool_msgs = [m for m in messages if m.get("role") == "tool"]
        if tool_msgs:
            last = str(tool_msgs[-1].get("content", ""))
            content = f"[mock] 计算结果是 {last}"
            return _finish(
                content=content,
                model_name=model_name,
                provider=self.provider,
                started=started,
                finish_reason="stop",
            )

        user_text = _last_user_content(messages)
        if not user_text.strip():
            raise ValueError("empty prompt")
        if user_text == "__bench_fail__":
            raise RuntimeError("simulated bench failure")

        # 第 1 轮：挂了 calculator 且话里像算式 → 模拟 tool_calls
        if "calculator" in tool_names:
            expr = _extract_expression(user_text)
            if expr is not None:
                args = json.dumps({"expression": expr}, ensure_ascii=False)
                return _finish(
                    content="",
                    model_name=model_name,
                    provider=self.provider,
                    started=started,
                    tool_calls=[
                        ToolCall(
                            id="call_mock_calc_1",
                            name="calculator",
                            arguments=args,
                        )
                    ],
                    finish_reason="tool_calls",
                    prompt_basis=user_text,
                )

        if response_format is not None:
            content = json.dumps(
                {
                    "answer": f"[mock-json] {user_text[:80]}",
                    "confidence": 0.85,
                    "sources": ["mock"],
                },
                ensure_ascii=False,
            )
        else:
            content = f"[mock] echo: {user_text}"

        return _finish(
            content=content,
            model_name=model_name,
            provider=self.provider,
            started=started,
            finish_reason="stop",
            prompt_basis=user_text,
        )


def _tool_names(tools: list[dict[str, Any]] | None) -> set[str]:
    if not tools:
        return set()
    names: set[str] = set()
    for item in tools:
        fn = item.get("function") or {}
        name = fn.get("name")
        if isinstance(name, str):
            names.add(name)
    return names


def _last_user_content(messages: list[dict[str, Any]]) -> str:
    for msg in reversed(messages):
        if msg.get("role") == "user":
            return str(msg.get("content") or "")
    return ""


def _extract_expression(text: str) -> str | None:
    match = _EXPR_RE.search(text)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(0)).strip()


def _finish(
    *,
    content: str,
    model_name: str,
    provider: str,
    started: float,
    tool_calls: list[ToolCall] | None = None,
    finish_reason: str | None = None,
    prompt_basis: str = "",
) -> ChatResult:
    prompt_tokens = max(1, len(prompt_basis or content) // 4)
    completion_tokens = max(1, len(content) // 4) if content else 1
    latency_ms = max(1, int((time.perf_counter() - started) * 1000))
    return ChatResult(
        content=content,
        model=model_name,
        provider=provider,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        latency_ms=latency_ms,
        tool_calls=list(tool_calls or ()),
        finish_reason=finish_reason,
    )
