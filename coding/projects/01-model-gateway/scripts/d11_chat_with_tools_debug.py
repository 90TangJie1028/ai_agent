"""D11 学习：真实 DeepSeek Function Calling 计算器闭环（可断点走查）。

运行（项目目录或仓库根均可，需 .env 里有 DEEPSEEK_API_KEY）:

    cd coding/projects/01-model-gateway
    ..\\..\\..\\.venv\\Scripts\\python.exe scripts/d11_chat_with_tools_debug.py

VS Code / Cursor: 用 launch「Debug: D11_chat_with_tools_debug.py」，
在下面标了「断点」的行停住，逐步看 variables。

流程（和笔记 07 一致）:
  ① 准备 tools + messages
  ② 第 1 次请求 API → tool_calls
  ③ 本地 registry.call（真正算数）
  ④ 拼回 assistant + role=tool
  ⑤ 第 2 次请求 API → 最终自然语言答案
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# 允许直接 python scripts/xxx.py（未 pip install -e 时）
_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from model_gateway.adapters.base import ChatResult
from model_gateway.gateway import ModelGateway
from model_gateway.tools.calculator import build_default_registry


USER_MESSAGE = "请计算 123 * 456"


def _dump(title: str, obj: Any) -> None:
    print(f"\n{'=' * 60}")
    print(title)
    print("=" * 60)
    if isinstance(obj, (dict, list)):
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    else:
        print(obj)


def step2_first_api(
    adapter: Any,
    tools: list[dict[str, Any]],
    messages: list[dict[str, Any]],
    model_name: str,
) -> ChatResult:
    """② 第 1 次真实请求 DeepSeek。← 可在 chat_messages 调用行断点，F11 进适配器"""
    print("\n>>> 正在请求 DeepSeek（第 1 轮，等待 tool_calls）...")
    # ↓ 断点建议打在下一行
    result = adapter.chat_messages(
        messages,
        model=model_name,
        tools=tools,
    )
    _dump(
        "② 第 1 轮响应摘要",
        {
            "finish_reason": result.finish_reason,
            "content": result.content,
            "tool_calls": [
                {"id": tc.id, "name": tc.name, "arguments": tc.arguments}
                for tc in result.tool_calls
            ],
            "tokens": {
                "prompt": result.prompt_tokens,
                "completion": result.completion_tokens,
                "total": result.total_tokens,
            },
            "latency_ms": result.latency_ms,
        },
    )
    if not result.tool_calls:
        raise SystemExit(
            "模型没有返回 tool_calls（直接答了）。"
            "可改 USER_MESSAGE 强调「必须用工具计算」，再跑一次。"
        )
    return result


def step3_local_execute(registry: Any, first: ChatResult) -> list[dict[str, Any]]:
    """③ 本地执行工具（模型不算数）。← 可在 registry.call 断点，F11 进 calculator"""
    tool_messages: list[dict[str, Any]] = []
    for tc in first.tool_calls:
        print(f"\n>>> 本地执行 tool={tc.name!r} id={tc.id!r}")
        print(f"    arguments(原始字符串) = {tc.arguments!r}")
        # ↓ 断点建议打在下一行：validate_args → run_calculator → eval_safe
        tool_out = registry.call(tc.name, tc.arguments)
        tool_content = str(tool_out)
        print(f"    本地结果 = {tool_content!r}")
        tool_messages.append(
            {
                "role": "tool",
                "tool_call_id": tc.id,
                "content": tool_content,
            }
        )
    return tool_messages


def step4_append_history(
    messages: list[dict[str, Any]],
    first: ChatResult,
    tool_messages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """④ 把 assistant(tool_calls) + tool(结果) 拼进历史。← 可在此断点看 messages"""
    assistant_msg = first.to_assistant_message()
    messages.append(assistant_msg)
    messages.extend(tool_messages)
    _dump("④ 第 2 次请求前的完整 messages", messages)
    return messages


def step5_second_api(
    adapter: Any,
    tools: list[dict[str, Any]],
    messages: list[dict[str, Any]],
    model_name: str,
) -> ChatResult:
    """⑤ 第 2 次真实请求 → 最终答案。← 可在 chat_messages 断点"""
    print("\n>>> 正在请求 DeepSeek（第 2 轮，等待最终答案）...")
    # ↓ 断点建议打在下一行
    result = adapter.chat_messages(
        messages,
        model=model_name,
        tools=tools,
    )
    _dump(
        "⑤ 第 2 轮响应（最终）",
        {
            "finish_reason": result.finish_reason,
            "content": result.content,
            "tool_calls": [
                {"id": tc.id, "name": tc.name, "arguments": tc.arguments}
                for tc in result.tool_calls
            ],
            "tokens": {
                "prompt": result.prompt_tokens,
                "completion": result.completion_tokens,
                "total": result.total_tokens,
            },
            "latency_ms": result.latency_ms,
        },
    )
    return result


def main() -> None:
    print("D11 DeepSeek FC 走查开始")
    print(f"用户问题: {USER_MESSAGE!r}")
    print("对照: Cursor Agent 调 Shell → 本地执行 → 结果回对话 → 模型继续写")

    # ① 准备（同一份 registry，避免重复注册）
    gateway = ModelGateway(provider="deepseek")
    if "deepseek" not in gateway.available_providers:
        raise SystemExit("未配置 DEEPSEEK_API_KEY，请检查仓库根目录 .env")

    registry = build_default_registry()
    tools = registry.to_openai_tools()
    messages: list[dict[str, Any]] = [{"role": "user", "content": USER_MESSAGE}]
    model_name = gateway._providers["deepseek"].default_model  # noqa: SLF001
    adapter = gateway._adapters["deepseek"]  # noqa: SLF001

    _dump("① tools（给模型看的工具字典）", tools)
    _dump("① messages（第 1 次请求）", messages)
    print(f"\nprovider=deepseek  model={model_name}")

    # ② 第 1 次 API
    first = step2_first_api(adapter, tools, messages, model_name)

    # ③ 本地执行
    tool_messages = step3_local_execute(registry, first)

    # ④ 拼历史
    messages = step4_append_history(messages, first, tool_messages)

    # ⑤ 第 2 次 API
    final = step5_second_api(adapter, tools, messages, model_name)

    print("\n" + "#" * 60)
    print("最终答案:")
    print(final.content)
    print("#" * 60)
    print(
        "\n可选对照：gateway 一键封装同一流程 →\n"
        "  ModelGateway(provider='deepseek').chat_with_tools(USER_MESSAGE)"
    )


if __name__ == "__main__":
    main()
