"""metrics：CallRecord、cost 折算、MetricsCollector。"""

from unittest.mock import MagicMock, patch

import pytest

from model_gateway.config import ProviderConfig
from model_gateway.gateway import ModelGateway
from model_gateway.metrics import (
    CallRecord,
    MetricsCollector,
    compute_cost_usd,
    load_pricing,
)


@pytest.fixture
def deepseek_config() -> ProviderConfig:
    return ProviderConfig(
        name="deepseek",
        api_key="test-key",
        base_url="https://api.deepseek.com/v1",
        default_model="deepseek-chat",
    )


def test_compute_cost_deepseek():
    pricing = load_pricing()
    # 10 prompt + 5 completion @ deepseek-chat rates
    cost = compute_cost_usd("deepseek-chat", 10, 5, pricing=pricing)
    expected = (10 * 0.14 + 5 * 0.28) / 1_000_000
    assert cost == pytest.approx(expected)


def test_compute_cost_unknown_model_uses_default():
    pricing = load_pricing()
    cost = compute_cost_usd("unknown-model-xyz", 1_000_000, 0, pricing=pricing)
    assert cost == pytest.approx(1.0)


def test_gateway_chat_returns_call_record(deepseek_config: ProviderConfig):
    mock_response = MagicMock()
    mock_response.model = "deepseek-chat"
    mock_response.choices = [MagicMock(message=MagicMock(content="hi"))]
    mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=5, total_tokens=15)

    # 作用：临时用 mock 替换 `model_gateway.gateway.load_providers`，让它返回 {"deepseek": deepseek_config}
    # 类比 TypeScript：jest.spyOn(gateway, 'load_providers').mockReturnValue(...)
    # 类比 C++：gmock 设置方法桩返回值
    # 区别：Python 用 with 语法自动恢复（作用域内有效），TS/Java 需手动 restore
    with patch("model_gateway.gateway.load_providers", return_value={"deepseek": deepseek_config}):
        with patch("model_gateway.adapters.openai_compat.OpenAI") as mock_openai_cls:
            mock_client = mock_openai_cls.return_value
            mock_client.chat.completions.create.return_value = mock_response

            gateway = ModelGateway(provider="deepseek")
            gw = gateway.chat("你好")

    record = gw.record
    assert record.total_tokens > 0
    assert record.prompt_tokens == 10
    assert record.completion_tokens == 5
    assert record.success is True
    assert record.error_type is None
    assert record.cost_usd > 0
    assert record.latency_ms >= 0
    assert gw.result.content == "hi"


def test_gateway_chat_failure_returns_record(deepseek_config: ProviderConfig):
    with patch("model_gateway.gateway.load_providers", return_value={"deepseek": deepseek_config}):
        with patch("model_gateway.adapters.openai_compat.OpenAI") as mock_openai_cls:
            mock_client = mock_openai_cls.return_value
            mock_client.chat.completions.create.side_effect = TimeoutError("boom")

            gateway = ModelGateway(provider="deepseek")
            gw = gateway.chat("你好")

    assert gw.result is None
    assert gw.record.success is False
    assert gw.record.error_type == "TimeoutError"
    assert gw.record.total_tokens == 0


def test_call_record_from_error():
    record = CallRecord.from_error(
        provider="deepseek",
        model="deepseek-chat",
        exc=TimeoutError("boom"),
        latency_ms=100,
    )
    assert record.success is False
    assert record.error_type == "TimeoutError"
    assert record.total_tokens == 0
    assert record.cost_usd == 0.0


def test_metrics_collector_summary():
    collector = MetricsCollector()
    collector.add(
        CallRecord(
            provider="deepseek",
            model="deepseek-chat",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            latency_ms=100,
            cost_usd=0.001,
            success=True,
        )
    )
    collector.add(
        CallRecord(
            provider="deepseek",
            model="deepseek-chat",
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            latency_ms=0,
            cost_usd=0.0,
            success=False,
            error_type="TimeoutError",
        )
    )
    summary = collector.summary()
    assert summary["count"] == 2
    assert summary["success_count"] == 1
    assert summary["success_rate"] == pytest.approx(0.5)
    assert summary["total_tokens"] == 15
    assert summary["total_cost_usd"] == pytest.approx(0.001)
    assert summary["p95_latency_ms"] == 100
