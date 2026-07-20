"""D12：Moonshot 第二适配器 + 按 provider 路由。"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from model_gateway.config import ProviderConfig
from model_gateway.gateway import ModelGateway


@pytest.fixture
def dual_providers() -> dict[str, ProviderConfig]:
    return {
        "deepseek": ProviderConfig(
            name="deepseek",
            api_key="ds-key",
            base_url="https://api.deepseek.com/v1",
            default_model="deepseek-chat",
        ),
        "moonshot": ProviderConfig(
            name="moonshot",
            api_key="ms-key",
            base_url="https://api.moonshot.cn/v1",
            default_model="kimi-k2.6",
        ),
    }


def test_gateway_lists_moonshot_when_configured(dual_providers: dict[str, ProviderConfig]):
    with patch("model_gateway.gateway.load_providers", return_value=dual_providers):
        gateway = ModelGateway(provider="deepseek")
        assert gateway.available_providers == ["deepseek", "mock", "moonshot"]


def test_chat_routes_to_moonshot_adapter(dual_providers: dict[str, ProviderConfig]):
    mock_response = MagicMock()
    mock_response.model = "kimi-k2.6"
    mock_response.choices = [MagicMock(message=MagicMock(content="pong", tool_calls=None))]
    mock_response.usage = MagicMock(prompt_tokens=3, completion_tokens=1, total_tokens=4)

    with patch("model_gateway.gateway.load_providers", return_value=dual_providers):
        with patch("model_gateway.adapters.openai_compat.OpenAI") as mock_openai_cls:
            mock_client = mock_openai_cls.return_value
            mock_client.chat.completions.create.return_value = mock_response

            gateway = ModelGateway(provider="deepseek")
            gw = gateway.chat("ping", provider="moonshot")

    assert gw.result is not None
    assert gw.result.provider == "moonshot"
    assert gw.result.model == "kimi-k2.6"
    assert gw.result.content == "pong"

    # OpenAI SDK 用 moonshot 的 base_url / key 初始化
    kwargs = mock_openai_cls.call_args.kwargs
    assert kwargs["api_key"] == "ms-key"
    assert kwargs["base_url"] == "https://api.moonshot.cn/v1"


def test_same_prompt_can_target_either_provider(dual_providers: dict[str, ProviderConfig]):
    """同一 prompt，provider 参数决定走哪条适配器（不联网）。"""
    prompt = "用一个词回答：你好"

    def _fake_response(model: str, content: str) -> MagicMock:
        resp = MagicMock()
        resp.model = model
        resp.choices = [MagicMock(message=MagicMock(content=content, tool_calls=None))]
        resp.usage = MagicMock(prompt_tokens=5, completion_tokens=2, total_tokens=7)
        return resp

    with patch[MagicMock | AsyncMock]("model_gateway.gateway.load_providers", return_value=dual_providers):
        with patch("model_gateway.adapters.openai_compat.OpenAI") as mock_openai_cls:
            mock_client = mock_openai_cls.return_value
            mock_client.chat.completions.create.side_effect = [
                _fake_response("deepseek-chat", "deepseek-ok"),
                _fake_response("kimi-k2.6", "moonshot-ok"),
            ]

            gateway = ModelGateway(provider="deepseek")
            ds = gateway.chat(prompt, provider="deepseek")
            ms = gateway.chat(prompt, provider="moonshot")

    assert ds.result is not None and ms.result is not None
    assert ds.result.provider == "deepseek"
    assert ms.result.provider == "moonshot"
    assert ds.result.content == "deepseek-ok"
    assert ms.result.content == "moonshot-ok"


@pytest.mark.integration
def test_dual_provider_live_same_prompt():
    """同一 prompt 各调 1 次。手动: pytest -m integration tests/test_moonshot_routing.py"""
    gateway = ModelGateway()
    missing = [p for p in ("deepseek", "moonshot") if p not in gateway.available_providers]
    if missing:
        pytest.skip(f"未配置: {', '.join(missing)}")

    prompt = "只回复两个字：收到"
    ds = gateway.chat(prompt, provider="deepseek")
    ms = gateway.chat(prompt, provider="moonshot")

    assert ds.result is not None and ds.record.success
    assert ms.result is not None and ms.record.success
    assert ds.result.provider == "deepseek"
    assert ms.result.provider == "moonshot"
    assert ds.result.content.strip()
    assert ms.result.content.strip()
    assert ds.record.total_tokens > 0
    assert ms.record.total_tokens > 0
