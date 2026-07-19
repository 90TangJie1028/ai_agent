"""calculator：安全求值 + 注册到 ToolRegistry。"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from model_gateway.tools.calculator import (
    CalcArgs,
    UnsafeExpressionError,
    build_default_registry,
    eval_safe,
    register_calculator,
    run_calculator,
)
from model_gateway.tools.registry import ToolRegistry


def test_eval_safe_basic_ops():
    assert eval_safe("1+2*3") == 7
    assert eval_safe("(1+2)*3") == 9
    assert eval_safe("123 * 456") == 56088
    assert eval_safe("-3 + 5") == 2
    assert eval_safe("10 // 3") == 3
    assert eval_safe("10 % 3") == 1
    assert eval_safe("2 ** 3") == 8


def test_eval_safe_float_div():
    assert eval_safe("1 / 2") == 0.5


def test_eval_safe_rejects_empty():
    with pytest.raises(ValueError, match="non-empty"):
        eval_safe("   ")


def test_eval_safe_rejects_names_and_calls():
    with pytest.raises(UnsafeExpressionError):
        eval_safe("__import__('os').system('echo hi')")
    with pytest.raises(UnsafeExpressionError):
        eval_safe("abs(1)")
    with pytest.raises(UnsafeExpressionError):
        eval_safe("x + 1")


def test_eval_safe_division_by_zero():
    with pytest.raises(ValueError, match="division by zero"):
        eval_safe("1/0")


def test_run_calculator_returns_string():
    assert run_calculator(CalcArgs(expression="123 * 456")) == "56088"
    assert run_calculator(CalcArgs(expression="1/2")) == "0.5"


def test_register_and_call_via_registry():
    reg = ToolRegistry()
    register_calculator(reg)
    assert "calculator" in reg.names()
    tools = reg.to_openai_tools()
    assert tools[0]["function"]["name"] == "calculator"
    assert reg.call("calculator", {"expression": "9*9"}) == "81"


def test_build_default_registry():
    reg = build_default_registry()
    assert reg.call("calculator", '{"expression":"10+2"}') == "12"


def test_calc_args_rejects_empty_expression():
    with pytest.raises(ValidationError):
        CalcArgs(expression="")
