"""结构化输出编排：拼 prompt、拼 API 参数、解析 LLM 响应。

本模块属于 **Gateway 编排层**，不属于 Adapter 传输层。

职责边界
--------
- 这里：根据 mode 决定「约束写进 prompt」还是「约束写进 response_format」；拿回字符串后再 parse + validate
- 不在：发 HTTP、重试 429、记 CallRecord（那些分别在 adapter / gateway.chat）

典型调用链（gateway.chat_structured）
------------------------------------
    build_structured_prompt(message, mode, response_model)  → 发给模型的文本
    build_response_format(mode, response_model)             → 传给 adapter 的 API 参数（或 None）
        ↓
    gateway.chat(prompt, response_format=...)               → adapter 发包收包，返回纯文本 content
        ↓
    parse_structured_response(content, response_model)      → StructuredAnswer 等业务对象

三种 mode 对照
--------------
| mode         | prompt 里有无 schema | response_format     | 约束强度 |
| prompt       | 有（整段 JSON Schema） | None                | 弱，靠模型听话 |
| json_object  | 简短字段说明           | type=json_object    | 中，保证合法 JSON |
| json_schema  | 简短说明               | type=json_schema    | 强，生成期按 schema |

无论哪种 mode，最后都要 parse_structured_response —— API 约束不能替代 Pydantic 校验。
"""

from __future__ import annotations

import json
from typing import Any, Literal, TypeVar

from pydantic import BaseModel, ValidationError

# 结构化输出的三种策略；作为 chat_structured(mode=...) 的类型提示。
# Literal 表示只能是这三个字符串之一，类似 TS 的 type Mode = 'prompt' | 'json_object' | 'json_schema'
StructuredOutputMode = Literal["prompt", "json_object", "json_schema"]

# 泛型：parse 之后返回「与 response_model 相同」的 Pydantic 类型。
# 类似 TS 的 <T extends z.ZodType> parse(schema: T): z.infer<T>
T = TypeVar("T", bound=BaseModel)


def build_response_format(
    mode: StructuredOutputMode,
    response_model: type[BaseModel],
) -> dict[str, Any] | None:
    """生成 OpenAI 兼容 API 的 response_format 参数。

    给谁用
    ------
    gateway.chat_structured 在调 adapter 前调用，结果传给
    openai_compat.chat(..., response_format=...)。

    返回值
    ------
    - mode == "prompt"      → None（不传该字段，约束全靠 prompt 里的 schema）
    - mode == "json_object" → {"type": "json_object"}
    - mode == "json_schema" → {"type": "json_schema", "json_schema": {...}}

    参数
    ----
    mode: 与 build_structured_prompt 使用同一 mode，保持 prompt/API 策略一致
    response_model: 任意 Pydantic 模型；json_schema 模式会调用其 model_json_schema()

    注意
    ----
    - 本函数只「造 dict」，不发请求；Adapter 负责原样塞进 SDK
    - 部分厂商不支持 json_schema，调用可能 400，需在业务层 fallback 或换 mode
    - json_object 不保证字段名/类型，只保证输出是 JSON 对象

    示例
    ----
    >>> build_response_format("prompt", StructuredAnswer) is None
    True
    >>> build_response_format("json_object", StructuredAnswer)
    {'type': 'json_object'}
    """
    if mode == "prompt":
        # Path A：不在 API 层约束，返回 None 表示 adapter 不传 response_format
        return None
    if mode == "json_object":
        # Path B：只要求模型输出合法 JSON 对象，不绑定具体字段 schema
        return {"type": "json_object"}
    # Path C：Structured Outputs —— schema 来自 Pydantic，与 validate 同源，避免手写两份
    schema = response_model.model_json_schema()
    return {
        "type": "json_schema",
        "json_schema": {
            # API 要求的名字，用小写模型名即可
            "name": schema.get("title", response_model.__name__).lower(),
            # strict=True：尽量让模型严格遵守 schema（OpenAI 系语义）
            "strict": True,
            "schema": schema,
        },
    }


def build_structured_prompt(
    message: str,
    mode: StructuredOutputMode,
    response_model: type[BaseModel],
) -> str:
    """按 mode 拼装最终发给模型的 user 消息文本。

    给谁用
    ------
    gateway.chat_structured 在调用 gateway.chat 之前，把用户原始 message
    扩展成「带输出格式说明」的 prompt。

    三种 mode 的 prompt 策略
    ------------------------
    prompt:
        用户话 + 完整 JSON Schema（model_json_schema 序列化）
        → 约束全在文本里，与 D8 行为一致

    json_object:
        用户话 + 简短字段说明（answer / confidence / sources）
        → 细节靠 response_format=json_object，prompt 不宜过长

    json_schema:
        用户话 + 一句「按 schema 只输出 JSON」
        → 形状约束在 response_format 里，prompt 不重复贴大段 schema

    参数
    ----
    message: 用户原始问题（已通过 ChatRequest 校验非空）
    mode: 与 build_response_format 一致
    response_model: 用于 prompt 模式导出 schema；其他模式仅间接相关

    返回
    ----
    完整 prompt 字符串，原样作为 adapter.chat 的 message 参数。

    示例
    ----
    >>> p = build_structured_prompt("1+1=?", "json_object", StructuredAnswer)
    >>> "JSON" in p and "1+1=?" in p
    True
    """
    if mode == "prompt":
        schema_hint = json.dumps(response_model.model_json_schema(), ensure_ascii=False)
        return (
            f"{message}\n\n"
            f"请严格按以下 JSON Schema 回复，只输出 JSON，不要 markdown：\n"
            f"{schema_hint}"
        )
    if mode == "json_object":
        # DeepSeek 等厂商要求：json_object 模式下 prompt 里仍应提到 JSON
        return (
            f"{message}\n\n"
            f"请以 JSON 对象回复，包含字段 answer（字符串）、"
            f"confidence（0-1 数字）、sources（字符串数组）。只输出 JSON。"
        )
    # json_schema：schema 已在 response_format 里，prompt 保持短
    return f"{message}\n\n请按约定 schema 回复，只输出 JSON，不要 markdown。"


def parse_structured_response(content: str, response_model: type[T]) -> T:
    """把 LLM 返回的纯文本解析为校验过的 Pydantic 对象。

    给谁用
    ------
    gateway.chat_structured 在 adapter 返回 content 之后调用；
    成功则 answer.model_dump_json() 写回 GatewayResult。

    两步
    ----
    1. json.loads(content)  —— 语法层；失败抛 json.JSONDecodeError
    2. model_validate(...)  —— 形状层；失败抛 pydantic.ValidationError

    参数
    ----
    content: adapter 返回的原始字符串（应为 JSON，不应含 markdown 包裹）
    response_model: 目标类型，默认 StructuredAnswer，D10 后可换 ToolArgs 等

    返回
    ----
    通过校验的 Pydantic 实例；类型与 response_model 一致。

    谁负责 catch
    ------------
    本函数不吞异常。gateway.chat_structured 捕获后转 CallRecord.from_error，
    业务层看到 GatewayResult(result=None)。

    示例
    ----
    >>> parse_structured_response(
    ...     '{"answer":"42","confidence":0.9,"sources":[]}',
    ...     StructuredAnswer,
    ... ).answer
    '42'
    """
    # 故意拆成两行，方便 debug 时分别在 loads / validate 设断点
    data = json.loads(content)
    return response_model.model_validate(data)
