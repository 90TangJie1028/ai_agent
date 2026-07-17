"""ToolRegistry：注册、OpenAI tools 导出、参数校验。"""

from __future__ import annotations

import pytest
from pydantic import BaseModel, Field, ValidationError

from model_gateway.tools.registry import ToolRegistry


class CalcArgs(BaseModel):
    expression: str = Field(min_length=1, description="arithmetic expression")


def test_register_and_export_openai_tools():
    reg = ToolRegistry()
    reg.register(
        name="calculator",
        description="Evaluate a basic arithmetic expression.",
        args_model=CalcArgs,
    )
    tools = reg.to_openai_tools()
    assert len(tools) == 1
    item = tools[0]
    assert item["type"] == "function"
    assert item["function"]["name"] == "calculator"
    assert "arithmetic" in item["function"]["description"]
    schema = item["function"]["parameters"]
    assert schema["type"] == "object"
    assert "expression" in schema["properties"]
    assert "expression" in schema.get("required", [])


def test_validate_args_accepts_json_string_and_dict():
    reg = ToolRegistry()
    reg.register("calculator", "calc", CalcArgs)
    a = reg.validate_args("calculator", '{"expression":"1+2*3"}')
    b = reg.validate_args("calculator", {"expression": "1+2*3"})
    assert a.expression == "1+2*3"
    assert b.expression == "1+2*3"


def test_validate_args_rejects_missing_field():
    reg = ToolRegistry()
    reg.register("calculator", "calc", CalcArgs)
    with pytest.raises(ValidationError):
        reg.validate_args("calculator", {})


def test_validate_args_rejects_wrong_type():
    reg = ToolRegistry()
    reg.register("calculator", "calc", CalcArgs)
    with pytest.raises(ValidationError):
        reg.validate_args("calculator", {"expression": 123})


def test_validate_args_rejects_invalid_json_string():
    reg = ToolRegistry()
    reg.register("calculator", "calc", CalcArgs)
    with pytest.raises(ValidationError):
        reg.validate_args("calculator", "{not-json")


def test_duplicate_register_raises():
    reg = ToolRegistry()
    reg.register("calculator", "calc", CalcArgs)
    with pytest.raises(ValueError, match="already registered"):
        reg.register("calculator", "calc", CalcArgs)


def test_call_runs_handler_after_validate():
    reg = ToolRegistry()
    reg.register(
        "calculator",
        "calc",
        CalcArgs,
        handler=lambda args: f"ok:{args.expression}",
    )
    assert reg.call("calculator", {"expression": "9*9"}) == "ok:9*9"
