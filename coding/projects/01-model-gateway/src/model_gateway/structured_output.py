"""结构化输出：response_format 构建与 LLM 响应解析（Gateway 编排用）。"""

from __future__ import annotations

import json
from typing import Any, Literal, TypeVar

from pydantic import BaseModel, ValidationError

StructuredOutputMode = Literal["prompt", "json_object", "json_schema"]

T = TypeVar("T", bound=BaseModel)


def build_response_format(
    mode: StructuredOutputMode,
    response_model: type[BaseModel],
) -> dict[str, Any] | None:
    """按模式生成 API response_format；prompt 模式不传。"""
    if mode == "prompt":
        return None
    if mode == "json_object":
        return {"type": "json_object"}
    schema = response_model.model_json_schema()
    return {
        "type": "json_schema",
        "json_schema": {
            "name": schema.get("title", response_model.__name__).lower(),
            "strict": True,
            "schema": schema,
        },
    }


def build_structured_prompt(
    message: str,
    mode: StructuredOutputMode,
    response_model: type[BaseModel],
) -> str:
    """按模式拼装 prompt；schema 在 prompt 或 response_format 二选一/并用。"""
    if mode == "prompt":
        schema_hint = json.dumps(response_model.model_json_schema(), ensure_ascii=False)
        return (
            f"{message}\n\n"
            f"请严格按以下 JSON Schema 回复，只输出 JSON，不要 markdown：\n"
            f"{schema_hint}"
        )
    if mode == "json_object":
        return (
            f"{message}\n\n"
            f"请以 JSON 对象回复，包含字段 answer（字符串）、"
            f"confidence（0-1 数字）、sources（字符串数组）。只输出 JSON。"
        )
    return f"{message}\n\n请按约定 schema 回复，只输出 JSON，不要 markdown。"


def parse_structured_response(content: str, response_model: type[T]) -> T:
    """json.loads + Pydantic 校验；失败抛 JSONDecodeError / ValidationError。"""
    return response_model.model_validate(json.loads(content))
