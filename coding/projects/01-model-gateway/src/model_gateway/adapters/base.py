"""各厂商适配器共用接口。国内厂商多兼容 OpenAI Chat Completions 格式。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class ChatResult:
    content: str
    model: str
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0


class ChatAdapter(Protocol):
    provider: str

    def chat(self, message: str, *, model: str | None = None) -> ChatResult: ...
