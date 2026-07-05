"""schemas：Pydantic 模型与 JSON Schema 快照。"""

import json

import pytest
from pydantic import ValidationError
from unittest.mock import MagicMock, patch

from model_gateway.gateway import ModelGateway
from model_gateway.schemas import ChatRequest, StructuredAnswer
from model_gateway.structured_output import (
    build_response_format,
    parse_structured_response,
)
from model_gateway.config import ProviderConfig
from model_gateway.adapters.openai_compat import OpenAICompatAdapter
from model_gateway.retry import RetryPolicy


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


def test_chat_structured_json_object_mode_mock_succeeds():
    gateway = ModelGateway(provider="mock")
    gw = gateway.chat_structured("1+1=?", mode="json_object")
    assert gw.result is not None
    assert gw.record.success is True
    parsed = json.loads(gw.result.content)
    assert parsed["answer"]
    assert 0 <= parsed["confidence"] <= 1


def test_build_response_format_modes():
    assert build_response_format("prompt", StructuredAnswer) is None
    assert build_response_format("json_object", StructuredAnswer) == {"type": "json_object"}
    rf = build_response_format("json_schema", StructuredAnswer)
    assert rf is not None
    assert rf["type"] == "json_schema"
    assert rf["json_schema"]["strict"] is True


def test_openai_compat_passes_response_format():
    config = ProviderConfig(
        name="test",
        api_key="k",
        base_url="https://example.com",
        default_model="m",
    )
    adapter = OpenAICompatAdapter(config, retry_policy=RetryPolicy(max_retries=0))
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content='{"answer":"x","confidence":0.5}'))]
    mock_response.model = "m"
    mock_response.usage = None
    mock_client.chat.completions.create.return_value = mock_response
    adapter._client = mock_client

    rf = {"type": "json_object"}
    adapter.chat("hi", response_format=rf)

    kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert kwargs["response_format"] == rf


def test_parse_structured_response_rejects_invalid():
    with pytest.raises(json.JSONDecodeError):
        parse_structured_response("not json", StructuredAnswer)
