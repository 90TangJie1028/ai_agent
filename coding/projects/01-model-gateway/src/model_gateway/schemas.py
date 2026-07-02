"""Pydantic 业务模型：结构化输出、请求校验。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, description="user's message")
    provider: str | None = None
    model: str | None = None


class StructuredAnswer(BaseModel):
    answer: str = Field(..., description="model's answer")
    confidence: float = Field(ge=0, le=1, description="confidence of the model's answer")
    sources: list[str] = Field(default_factory=list, description="sources of the model's answer")
