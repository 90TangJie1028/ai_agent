"""ratelimit / async_chat 单元测试：令牌桶 QPS、10 路并发。"""

import asyncio
import time
from unittest.mock import MagicMock, patch

import pytest

from model_gateway.adapters.base import ChatResult
from model_gateway.config import ProviderConfig
from model_gateway.gateway import ModelGateway
from model_gateway.metrics import CallRecord, GatewayResult
from model_gateway.ratelimit import RateLimitConfig, TokenBucket


@pytest.fixture
def deepseek_config() -> ProviderConfig:
    return ProviderConfig(
        name="deepseek",
        api_key="test-key",
        base_url="https://api.deepseek.com/v1",
        default_model="deepseek-chat",
    )


@pytest.mark.asyncio
async def test_token_bucket_burst_then_wait():
    """burst=1, rate=5：连续 6 次 acquire 至少等待 ~1s。"""
    bucket = TokenBucket(rate=5.0, burst=1)
    started = time.perf_counter()
    for _ in range(6):
        await bucket.acquire()
    elapsed = time.perf_counter() - started
    assert elapsed >= 0.9


@pytest.mark.asyncio
async def test_token_bucket_burst_allows_spike():
    """burst=5：前 5 次应立即通过。"""
    bucket = TokenBucket(rate=2.0, burst=5)
    started = time.perf_counter()
    for _ in range(5):
        await bucket.acquire()
    elapsed = time.perf_counter() - started
    assert elapsed < 0.1


def test_token_bucket_from_config():
    bucket = TokenBucket.from_config(RateLimitConfig(rate=3.0, burst=6))
    assert bucket.rate == 3.0
    assert bucket.burst == 6


@pytest.mark.asyncio
async def test_async_chat_ten_concurrent(deepseek_config: ProviderConfig):
    """10 路 gather 全部成功，无异常。"""
    mock_response = MagicMock()
    mock_response.model = "deepseek-chat"
    mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]
    mock_response.usage = MagicMock(prompt_tokens=1, completion_tokens=1, total_tokens=2)

    limiter = TokenBucket(rate=100.0, burst=100)

    with patch("model_gateway.gateway.load_providers", return_value={"deepseek": deepseek_config}):
        with patch("model_gateway.adapters.openai_compat.OpenAI") as mock_openai_cls:
            mock_client = mock_openai_cls.return_value
            mock_client.chat.completions.create.return_value = mock_response

            gateway = ModelGateway(
                provider="deepseek",
                rate_limiter=limiter,
                max_concurrent=10,
            )
            results = await gateway.async_chat_batch([f"ping-{i}" for i in range(10)])

    assert len(results) == 10
    assert all(r.result.content == "ok" for r in results)
    assert mock_client.chat.completions.create.call_count == 10


@pytest.mark.asyncio
async def test_async_chat_respects_qps(deepseek_config: ProviderConfig):
    """rate=5, burst=1：10 次调用总耗时受 QPS 约束。"""
    mock_response = MagicMock()
    mock_response.model = "deepseek-chat"
    mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]
    mock_response.usage = MagicMock(prompt_tokens=1, completion_tokens=1, total_tokens=2)

    limiter = TokenBucket(rate=5.0, burst=1)

    with patch("model_gateway.gateway.load_providers", return_value={"deepseek": deepseek_config}):
        with patch("model_gateway.adapters.openai_compat.OpenAI") as mock_openai_cls:
            mock_client = mock_openai_cls.return_value
            mock_client.chat.completions.create.return_value = mock_response

            gateway = ModelGateway(
                provider="deepseek",
                rate_limiter=limiter,
                max_concurrent=10,
            )
            started = time.perf_counter()
            await gateway.async_chat_batch([f"msg-{i}" for i in range(10)])
            elapsed = time.perf_counter() - started

    assert mock_client.chat.completions.create.call_count == 10
    # 10 次、burst=1、rate=5 → 至少还需 9/5 ≈ 1.8s
    assert elapsed >= 1.5


@pytest.mark.asyncio
async def test_async_chat_mock_without_network(deepseek_config: ProviderConfig):
    """单路 async_chat 走 to_thread + mock。"""
    limiter = TokenBucket(rate=100.0, burst=100)

    with patch("model_gateway.gateway.load_providers", return_value={"deepseek": deepseek_config}):
        gateway = ModelGateway(provider="deepseek", rate_limiter=limiter, max_concurrent=10)

        fake = GatewayResult(
            result=ChatResult(
                content="mocked",
                model="deepseek-chat",
                provider="deepseek",
                total_tokens=3,
            ),
            record=CallRecord.from_chat_result(
                ChatResult(
                    content="mocked",
                    model="deepseek-chat",
                    provider="deepseek",
                    total_tokens=3,
                )
            ),
        )
        with patch.object(gateway, "chat", return_value=fake) as mock_chat:
            result = await gateway.async_chat("hello")

    assert result.result.content == "mocked"
    mock_chat.assert_called_once_with("hello", provider=None, model=None, timeout=None)
