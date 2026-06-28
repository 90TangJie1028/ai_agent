"""MockAdapter 集成测试：无需 API Key、无需 patch OpenAI SDK。"""

import pytest

from model_gateway.adapters.mock import MockAdapter
from model_gateway.gateway import ModelGateway


def test_mock_adapter_echo():
    adapter = MockAdapter()
    result = adapter.chat("hello", model="mock-model")
    assert result.content == "[mock] echo: hello"
    assert result.provider == "mock"
    assert result.total_tokens > 0


def test_gateway_chat_with_mock_provider():
    gateway = ModelGateway(provider="mock")
    assert "mock" in gateway.available_providers

    gw = gateway.chat("ping")
    assert gw.result is not None
    assert gw.result.content == "[mock] echo: ping"
    assert gw.record.success is True
    assert gw.record.provider == "mock"
    assert gw.record.total_tokens > 0


def test_mock_empty_prompt_fails():
    gateway = ModelGateway(provider="mock")
    gw = gateway.chat("")
    assert gw.result is None
    assert gw.record.success is False
    assert gw.record.error_type == "ValueError"


def test_mock_bench_fail_marker():
    gateway = ModelGateway(provider="mock")
    gw = gateway.chat("__bench_fail__")
    assert gw.result is None
    assert gw.record.success is False
    assert gw.record.error_type == "RuntimeError"


@pytest.mark.asyncio
async def test_gateway_async_chat_with_mock():
    gateway = ModelGateway(provider="mock")
    gw = await gateway.async_chat("async ping")
    assert gw.result is not None
    assert "[mock] echo: async ping" in gw.result.content


@pytest.mark.asyncio
async def test_gateway_async_chat_batch_with_mock():
    gateway = ModelGateway(provider="mock")
    results = await gateway.async_chat_batch(["a", "b"])
    assert len(results) == 2
    assert all(r.record.success for r in results)
