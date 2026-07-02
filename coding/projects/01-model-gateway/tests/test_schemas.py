"""schemas：Pydantic 模型与 JSON Schema 快照。"""

import json

import pytest
from pydantic import ValidationError

from model_gateway.gateway import ModelGateway
from model_gateway.schemas import ChatRequest, StructuredAnswer


def test_structured_answer_json_schema_snapshot():
    schema = StructuredAnswer.model_json_schema()
    assert schema["type"] == "object"
    assert schema["title"] == "StructuredAnswer"
    assert schema["required"] == ["answer", "confidence"]

    props = schema["properties"]
    assert props["answer"]["type"] == "string"
    assert props["confidence"]["type"] == "number"
    assert props["confidence"]["minimum"] == 0
    assert props["confidence"]["maximum"] == 1
    assert props["sources"]["type"] == "array"
    assert props["sources"]["items"]["type"] == "string"


def test_structured_answer_validate_and_dump():
    obj = StructuredAnswer.model_validate(
        {"answer": "42", "confidence": 0.95, "sources": ["doc1"]}
    )
    assert obj.model_dump() == {
        "answer": "42",
        "confidence": 0.95,
        "sources": ["doc1"],
    }
    parsed = json.loads(obj.model_dump_json())
    assert parsed["answer"] == "42"


def test_structured_answer_rejects_out_of_range_confidence():
    with pytest.raises(ValidationError) as exc_info:
        StructuredAnswer.model_validate({"answer": "x", "confidence": 1.5})
    errors = exc_info.value.errors()
    assert errors[0]["loc"] == ("confidence",)
    assert errors[0]["type"] == "less_than_equal"


def test_chat_request_rejects_empty_message():
    with pytest.raises(ValidationError):
        ChatRequest(message="")


def test_chat_request_exclude_none():
    req = ChatRequest(message="hello")
    assert req.model_dump(exclude_none=True) == {"message": "hello"}


def test_chat_structured_rejects_empty_message():
    gateway = ModelGateway(provider="mock")
    gw = gateway.chat_structured("")
    assert gw.result is None
    assert gw.record.success is False
    assert gw.record.error_type == "ValidationError"


def test_chat_structured_mock_non_json_fails_parse():
    gateway = ModelGateway(provider="mock")
    gw = gateway.chat_structured("1+1=?")
    assert gw.result is None
    assert gw.record.success is False
    assert gw.record.error_type == "JSONDecodeError"
