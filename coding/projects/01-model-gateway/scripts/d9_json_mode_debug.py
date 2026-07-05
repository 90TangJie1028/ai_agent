"""D9 学习：JSON mode vs Structured Outputs 概念走查。

运行: .venv\\Scripts\\python.exe scripts/d9_json_mode_debug.py

不发起网络请求；用模拟脏数据演示三条路径的差异与失败点。
"""
from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from model_gateway.schemas import StructuredAnswer


# ── 模拟 LLM 脏输出（Path A prompt-only 常见失败）────────────────────────────

DIRTY_RESPONSES: list[tuple[str, str]] = [
    ("合法 JSON", '{"answer": "42", "confidence": 0.9, "sources": []}'),
    ("markdown 包裹", '```json\n{"answer": "hi", "confidence": 0.5}\n```'),
    ("缺字段", '{"answer": "hi"}'),
    ("类型错", '{"answer": "hi", "confidence": "high", "sources": []}'),
    ("confidence 超界", '{"answer": "hi", "confidence": 1.5, "sources": []}'),
    ("多余文本", '这是答案：{"answer": "hi", "confidence": 0.8, "sources": []}'),
]


def simulate_parse(label: str, raw: str) -> None:
    """演示 chat_structured 第四步：json.loads → model_validate。"""
    print(f"\n--- {label} ---")
    print(f"raw: {raw[:80]}{'...' if len(raw) > 80 else ''}")
    try:
        data = json.loads(raw)
        answer = StructuredAnswer.model_validate(data)
        print(f"✅ OK → {answer.model_dump()}")
    except json.JSONDecodeError as e:
        print(f"❌ JSONDecodeError: {e.msg} (pos={e.pos})")
    except ValidationError as e:
        print(f"❌ ValidationError: {e.error_count()} issue(s)")
        for err in e.errors():
            print(f"   loc={err['loc']} type={err['type']} msg={err['msg']}")


def build_response_format_json_object() -> dict[str, Any]:
    """Path B：只要求合法 JSON 对象，不约束字段。"""
    return {"type": "json_object"}


def build_response_format_json_schema() -> dict[str, Any]:
    """Path C：Structured Outputs，生成期按 schema 约束。"""
    schema = StructuredAnswer.model_json_schema()
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "structured_answer",
            "strict": True,
            "schema": schema,
        },
    }


def print_api_payloads() -> None:
    print("\n=== API response_format 对照 ===")
    print("\nPath B — json_object（语法合法即可）:")
    print(json.dumps(build_response_format_json_object(), indent=2))

    print("\nPath C — json_schema（形状也约束）:")
    payload = build_response_format_json_schema()
    # schema 很长，只打印外壳
    print(json.dumps({k: v for k, v in payload.items() if k != "json_schema"}, indent=2))
    inner = payload["json_schema"]
    print(f"  json_schema.name = {inner['name']!r}")
    print(f"  json_schema.strict = {inner['strict']}")
    print(f"  json_schema.schema.properties = {list(inner['schema']['properties'].keys())}")


def print_retry_hint() -> None:
    print("\n=== 失败重试策略（概念）===")
    print("""
1. JSONDecodeError  → 重试，prompt 加「只输出 JSON，不要 markdown」
2. ValidationError  → 重试，附上 errors() 让模型修正；或换 json_schema 模式
3. 设 max_retries + 指数退避（gateway 已有 RetryPolicy，D9 实验可复用）
4. 仍失败 → CallRecord.from_error，业务层降级（纯文本 / 默认值）
""")


def main() -> None:
    print("=== D9：三条结构化输出路径 ===")
    print("""
Path A  prompt + schema_hint     → chat_structured() 现状
Path B  response_format=json_object
Path C  response_format=json_schema (Structured Outputs)
三条路径最后都要：json.loads + StructuredAnswer.model_validate
""")

    print("=== 1. 脏数据 parse 走查（模拟 Path A 失败）===")
    for label, raw in DIRTY_RESPONSES:
        simulate_parse(label, raw)

    print_api_payloads()
    print_retry_hint()

    print("\n=== 2. Path B 能修什么？===")
    print("json_object 在 API 层拒绝非 JSON 输出 → markdown 包裹、多余文本 通常消失")
    print("但缺字段、类型错、超界 → 仍 ValidationError，要靠 Path C 或重试")

    print("\n=== 3. 下一步（编码阶段）===")
    print("experiments/structured_vs_json.py：同一 prompt × 20 次 × A/B/C → 成功率表")


if __name__ == "__main__":
    main()
