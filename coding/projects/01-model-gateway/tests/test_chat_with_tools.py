"""chat_with_tools：mock 端到端 + 适配器 messages/tools。"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from model_gateway.adapters.base import ToolCall
from model_gateway.adapters.mock import MockAdapter
from model_gateway.config import ProviderConfig
from model_gateway.gateway import ModelGateway
from model_gateway.tools.calculator import build_default_registry


def test_mock_chat_messages_emits_calculator_tool_call():
    adapter = MockAdapter()
    tools = build_default_registry().to_openai_tools()
    result = adapter.chat_messages(
        [{"role": "user", "content": "请计算 123 * 456"}],
        tools=tools,
    )
    assert result.finish_reason == "tool_calls"
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].name == "calculator"
    assert "123" in result.tool_calls[0].arguments


def test_mock_chat_messages_second_round_uses_tool_result():
    adapter = MockAdapter()
    tools = build_default_registry().to_openai_tools()
    messages = [
        {"role": "user", "content": "请计算 123 * 456"},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "calculator",
                        "arguments": '{"expression":"123 * 456"}',
                    },
                }
            ],
        },
        {"role": "tool", "tool_call_id": "call_1", "content": "56088"},
    ]
    result = adapter.chat_messages(messages, tools=tools)
    assert result.finish_reason == "stop"
    assert "56088" in result.content
    assert result.tool_calls == []


def test_gateway_chat_with_tools_calculator_e2e_mock():
    gw = ModelGateway(provider="mock")
    result = gw.chat_with_tools(
        "请计算 123 * 456",
        registry=build_default_registry(),
        provider="mock",
    )
    assert result.record.success
    assert result.result is not None
    assert "56088" in result.result.content
    # 两轮 API：token / latency 应累加 > 单轮
    assert result.record.total_tokens >= 2


def test_gateway_chat_with_tools_no_expression_echoes():
    """没有算式时 mock 不强制 tool_calls，直接 echo。"""
    gw = ModelGateway(provider="mock")
    result = gw.chat_with_tools("你好", registry=build_default_registry(), provider="mock")
    assert result.result is not None
    assert "echo" in result.result.content
    assert result.result.tool_calls == []


@pytest.fixture
def deepseek_config() -> ProviderConfig:
    return ProviderConfig(
        name="deepseek",
        api_key="test-key",
        base_url="https://api.deepseek.com/v1",
        default_model="deepseek-chat",
    )


def test_openai_compat_parses_tool_calls(deepseek_config: ProviderConfig):
    mock_fn = MagicMock()
    mock_fn.name = "calculator"
    mock_fn.arguments = '{"expression":"1+2"}'
    mock_tc = MagicMock()
    mock_tc.id = "call_x"
    mock_tc.function = mock_fn

    mock_message = MagicMock()
    mock_message.content = None
    mock_message.tool_calls = [mock_tc]

    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_choice.finish_reason = "tool_calls"

    mock_response = MagicMock()
    mock_response.model = "deepseek-chat"
    mock_response.choices = [mock_choice]
    mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=5, total_tokens=15)

    with patch("model_gateway.adapters.openai_compat.OpenAI") as mock_openai_cls:
        mock_client = mock_openai_cls.return_value
        mock_client.chat.completions.create.return_value = mock_response

        from model_gateway.adapters.openai_compat import OpenAICompatAdapter

        adapter = OpenAICompatAdapter(deepseek_config)
        tools = build_default_registry().to_openai_tools()
        result = adapter.chat_messages(
            [{"role": "user", "content": "1+2"}],
            tools=tools,
        )

    assert result.tool_calls == [
        ToolCall(id="call_x", name="calculator", arguments='{"expression":"1+2"}')
    ]
    assert result.finish_reason == "tool_calls"
    create_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert create_kwargs["tools"] == tools


@pytest.mark.integration
def test_chat_with_tools_live_deepseek():
    """手动: pytest -m integration tests/test_chat_with_tools.py"""
    gateway = ModelGateway()
    if "deepseek" not in gateway.available_providers:
        pytest.skip("未配置 DEEPSEEK_API_KEY")
    gw = gateway.chat_with_tools(
        "请只用工具计算 123 * 456，并给出数字答案",
        provider="deepseek",
    )
    assert gw.result is not None
    assert gw.record.success
    assert "56088" in gw.result.content.replace(",", "").replace(" ", "")
