"""D8 学习：Pydantic v2 方法走查。运行: .venv\\Scripts\\python.exe scripts/d8_pydantic_debug.py"""
from __future__ import annotations

import json

from pydantic import BaseModel, Field, ValidationError


class StructuredAnswer(BaseModel):
    answer: str = Field(..., description="模型给出的最终答案")
    # ge: greater or equal; le: less or equal
    # gt: greater than;  lt: less than
    confidence: float = Field(ge=0, le=1, description="置信度 0-1")
    # sources：来源列表；模型回答用到的文档/证据出处。例如 ["文档1", "网页链接"]，可为空代表未引用具体来源。
    sources: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    provider: str | None = None
    model: str | None = None


def main() -> None:
    print("=== 1. 合法构造 StructuredAnswer ===")
    ok = StructuredAnswer(answer="42", confidence=0.95)
    print(repr(ok))

    print("\n=== 2. model_validate：dict → 对象 ===")
    parsed = StructuredAnswer.model_validate(
        {"answer": "hello", "confidence": 0.8, "sources": ["doc1"]}
    )
    print(parsed)

    print("\n=== 3. ValidationError：confidence 超界 ===")
    try:
        StructuredAnswer.model_validate({"answer": "x", "confidence": 1.5})
    except ValidationError as e:
        print(f"error_count={e.error_count()}")
        for err in e.errors():
            print(f"  loc={err['loc']} type={err['type']} msg={err['msg']}")

    print("\n=== 4. model_dump / model_dump_json ===")
    print("dump:", parsed.model_dump())
    print("json:", parsed.model_dump_json())

    print("\n=== 5. model_json_schema（给 LLM response_format / tools）===")
    schema = StructuredAnswer.model_json_schema()
    print(json.dumps(schema, indent=2, ensure_ascii=False))

    print("\n=== 6. ChatRequest：exclude_none ===")
    req = ChatRequest(message="hello")
    print(req.model_dump(exclude_none=True))


if __name__ == "__main__":
    main()
