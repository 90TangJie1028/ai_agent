from unittest.mock import MagicMock, patch

import pytest

from model_gateway.config import ProviderConfig
from model_gateway.gateway import ModelGateway


# 这个 pytest.fixture 装饰器的作用是将下面的函数 deepseek_config 注册为一个“测试夹具”。
# 测试夹具用于为测试用例提供预置的数据或对象，pytest 会在需要时自动传递该夹具的返回值给测试函数。
@pytest.fixture
def deepseek_config() -> ProviderConfig:
    return ProviderConfig(
        name="deepseek",
        api_key="test-key",
        base_url="https://api.deepseek.com/v1",
        default_model="deepseek-chat",
    )


# 这是 pytest 的一个标记（marker），用于将 test_gateway_lists_deepseek_when_configured 测试用例打上 abc 标签。
# 这样可以通过命令行参数（如 pytest -m abc）只运行带有 @pytest.mark.abc 标记的测试用例。
# 发现参数deepseek_config 会去找同名 @pytest.fixture 装饰的函数。
@pytest.mark.abc
def test_gateway_lists_deepseek_when_configured(deepseek_config: ProviderConfig):
    with patch("model_gateway.gateway.load_providers", return_value={"deepseek": deepseek_config}):
        gateway = ModelGateway(provider="deepseek")
        assert gateway.available_providers == ["deepseek"]


def test_gateway_chat_mock(deepseek_config: ProviderConfig):
    mock_response = MagicMock()
    mock_response.model = "deepseek-chat"
    mock_response.choices = [MagicMock(message=MagicMock(content="你好，我是 Agent"))]
    mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=5, total_tokens=15)

    with patch("model_gateway.gateway.load_providers", return_value={"deepseek": deepseek_config}):
        with patch("model_gateway.adapters.openai_compat.OpenAI") as mock_openai_cls:
            mock_client = mock_openai_cls.return_value
            mock_client.chat.completions.create.return_value = mock_response

            gateway = ModelGateway(provider="deepseek")
            result = gateway.chat("你好")

    assert result.content == "你好，我是 Agent"
    assert result.provider == "deepseek"
    assert result.total_tokens == 15


# 这是 pytest 的一个标记（marker），用于将 test_gateway_chat_live 测试用例打上 integration 标签。
# 这样可以通过命令行参数（如 pytest -m integration）只运行带有 @pytest.mark.integration 标记的集成测试。
@pytest.mark.integration
def test_gateway_chat_live():
    """手动执行: pytest -m integration coding/projects/01-model-gateway/tests/test_gateway_smoke.py"""
    gateway = ModelGateway()
    if "deepseek" not in gateway.available_providers:
        pytest.skip("未配置 DEEPSEEK_API_KEY")

    result = gateway.chat("回复 OK 两个字母")
    assert result.content
    assert result.total_tokens > 0
