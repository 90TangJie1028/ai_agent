"""各厂商适配器共用接口。国内厂商多兼容 OpenAI Chat Completions 格式。"""

# 这行的意思是：从 Python 的 __future__ 模块导入 annotations 特性，使得在本文件中，
# 类型注解会以字符串的形式存储和处理（即 "延迟求值" 注解），
# 这样在类型注解中可以引用当前作用域下还未定义的类名、类型等，
# 提升代码的兼容性和灵活性。常用于需要提前引用还没定义的类/类型，或为支持新版 typing 语法做准备。
from __future__ import annotations

# 意思是导入 Python 的 dataclasses 模块中的 dataclass 装饰器，用于简化数据类的定义
# dataclass 是 Python 为简化数据类（即主要用于存储数据的类）定义而引入的一个装饰器。其作用是自动为类生成如 __init__、__repr__、__eq__ 等方法，减少样板代码。
# dataclasses 是包含 dataclass 装饰器以及相关工具函数（如 field、asdict 等）的标准库模块，专门用于数据类的创建和操作。
from dataclasses import dataclass, field
# typing 标准库：Any 表示任意类型（类似 TypeScript 的 any），
# Protocol 用于定义结构化接口（鸭子类型），让适配器可灵活实现。
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ToolCall:
    """模型声明的一次工具调用（对应 API 的 tool_calls[] 一项）。"""

    id: str
    name: str
    arguments: str  # JSON 字符串；尚未 validate


@dataclass
class ChatResult:
    """一次 chat / chat_messages 调用的结果。"""

    content: str
    model: str
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    # D11：有工具调用时非空；最终自然语言答案时通常为空列表
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str | None = None

    def to_assistant_message(self) -> dict[str, Any]:
        """拼回 messages 历史用的 assistant 消息（含 tool_calls）。"""
        msg: dict[str, Any] = {
            "role": "assistant",
            "content": self.content if self.content else None,
        }
        if self.tool_calls:
            # 这是列表推导式（List Comprehension）的语法糖
            # 等价于：
            #   result = []
            #   for tc in self.tool_calls:
            #       result.append({
            #           "id": tc.id,
            #           "type": "function",
            #           "function": {"name": tc.name, "arguments": tc.arguments},
            #       })
            #   msg["tool_calls"] = result
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": tc.arguments},
                }
                for tc in self.tool_calls
            ]
        return msg

class ChatAdapter(Protocol):
    provider: str

    def chat(
        self,
        message: str,
        *,
        model: str | None = None,
        timeout: float | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> ChatResult:
        """单轮 user 文本对话。"""
        ...

    def chat_messages(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        timeout: float | None = None,
        tools: list[dict[str, Any]] | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> ChatResult:
        """多轮 messages（可带 tools），供 Function Calling 闭环使用。"""
        ...
