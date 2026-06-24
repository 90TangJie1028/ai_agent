"""retry 模块单元测试：429 退避重试、超时转 TimeoutError。"""

from unittest.mock import MagicMock, patch

# httpx 是一个现代的 Python HTTP 客户端库，类似于 TypeScript/JavaScript 里的 axios，C++/Java 常见的 HTTP 客户端（如 OkHttp/HttpClient）。
# 它用于发送 HTTP 请求、处理响应，支持异步、连接池和更丰富的用法，比 Python 内置 requests 更现代（但语义接近）。
import httpx
import pytest
from openai import APITimeoutError, RateLimitError

from model_gateway.adapters.openai_compat import OpenAICompatAdapter
from model_gateway.config import ProviderConfig
from model_gateway.retry import RetryPolicy, backoff_delay, is_retryable, with_retry


def _rate_limit_error() -> RateLimitError:
    request = httpx.Request("POST", "https://api.deepseek.com/v1/chat/completions")
    # httpx.Response(status_code, request=...)：
    # - 429: HTTP 状态码，表示“Too Many Requests”（被限流）
    # - request=request: 绑定本次响应对应的 httpx.Request 实例
    response = httpx.Response(429, request=request)
    return RateLimitError("rate limited", response=response, body=None)


def _timeout_error() -> APITimeoutError:
    request = httpx.Request("POST", "https://api.deepseek.com/v1/chat/completions")
    return APITimeoutError(request=request)


# @pytest.fixture 是 pytest 测试框架提供的装饰器，用来**声明一个测试夹具（fixture）**。
# 夹具可以为测试用例提供“依赖注入”——比如准备配置、测试数据、环境，自动清理资源等。
# 测试函数只要参数名写成 fixture 的名字，pytest 会自动调用它，把返回值注入过去。
# 可以类比 TypeScript 的依赖注入工厂、C++/Java 的测试 setUp 方法（但 pytest 更灵活、细粒度）。
# 没错，就是像昨天 pytest 支持的 @pytest.mark 的标记一样，运行 launch.json 里可以带 -m 参数来筛选执行哪些带 mark 的测试（比如 pytest -m "slow"）、只跑特定的分组
@pytest.fixture
def deepseek_config() -> ProviderConfig:
    return ProviderConfig(
        name="deepseek",
        api_key="test-key",
        base_url="https://api.deepseek.com/v1",
        default_model="deepseek-chat",
    )


def test_is_retryable_429():
    assert is_retryable(_rate_limit_error()) is True


def test_backoff_delay_exponential():
    policy = RetryPolicy(base_delay_sec=0.5, max_delay_sec=8.0)
    assert backoff_delay(0, policy) == 0.5
    assert backoff_delay(1, policy) == 1.0
    assert backoff_delay(2, policy) == 2.0
    assert backoff_delay(10, policy) == 8.0


# 这是 pytest 提供的 mock 装饰器 patch，用于“替换/模拟”指定模块 (`model_gateway.retry.time.sleep`) 里的 `sleep` 函数——防止测试实际等待，可以统计 sleep 次数和参数。
# 类比 TypeScript 里的 jest.mock("...") 或 jest.spyOn(...)
@patch("model_gateway.retry.time.sleep")
def test_with_retry_recovers_after_429(mock_sleep):
    calls = {"n": 0}

    @with_retry(RetryPolicy(max_retries=3, base_delay_sec=0.01))
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise _rate_limit_error()
        return "ok"

    assert flaky() == "ok"
    assert calls["n"] == 3
    assert mock_sleep.call_count == 2


@patch("model_gateway.retry.time.sleep")
def test_with_retry_exhausts_after_three_retries(mock_sleep):
    calls = {"n": 0}

    @with_retry(RetryPolicy(max_retries=3, base_delay_sec=0.01))
    def always_429():
        calls["n"] += 1
        raise _rate_limit_error()

    # 这一行的含义是：断言 with 块中的代码会抛出 RateLimitError 异常。如果没有抛出，测试会失败。
    # 类比 TypeScript 的 expect(() => ...).toThrow(RateLimitError) 或 Java 的 assertThrows。
    with pytest.raises(RateLimitError):
        always_429()
    assert calls["n"] == 4  # 1 次初始 + 3 次重试


def test_with_retry_timeout_raises_timeout_error():
    @with_retry()
    def slow():
        raise _timeout_error()

    with pytest.raises(TimeoutError):
        slow()


@patch("model_gateway.adapters.openai_compat.time.sleep")
def test_adapter_retries_429_three_times(mock_sleep, deepseek_config: ProviderConfig):
    mock_response = MagicMock()
    mock_response.model = "deepseek-chat"
    mock_response.choices = [MagicMock(message=MagicMock(content="重试成功"))]
    mock_response.usage = MagicMock(prompt_tokens=1, completion_tokens=1, total_tokens=2)

    side_effects = [_rate_limit_error(), _rate_limit_error(), mock_response]

    adapter = OpenAICompatAdapter(
        deepseek_config,
        retry_policy=RetryPolicy(max_retries=3, base_delay_sec=0.01),
    )
    with patch.object(adapter._client.chat.completions, "create", side_effect=side_effects) as mock_create:
        result = adapter.chat("ping")

    assert result.content == "重试成功"
    assert mock_create.call_count == 3
    assert mock_sleep.call_count == 2


@patch("model_gateway.adapters.openai_compat.time.sleep")
def test_adapter_timeout_raises_timeout_error(mock_sleep, deepseek_config: ProviderConfig):
    adapter = OpenAICompatAdapter(deepseek_config)
    with patch.object(
        adapter._client.chat.completions,
        "create",
        side_effect=_timeout_error(),
    ):
        with pytest.raises(TimeoutError):
            adapter.chat("ping", timeout=0.1)
