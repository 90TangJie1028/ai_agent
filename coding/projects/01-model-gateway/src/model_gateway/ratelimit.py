"""客户端限流：令牌桶算法，async acquire 排队等待。"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitConfig:
    """令牌桶静态配置。"""

    rate: float  # 每秒补充 token 数（QPS）
    burst: int  # 桶容量（突发上限）


class TokenBucket:
    """令牌桶：有 token 立即通过，不足时 async 等待补充。"""

    def __init__(self, rate: float, burst: int | None = None) -> None:
        if rate <= 0:
            raise ValueError("rate 必须 > 0")
        self._rate = rate
        # 判断 burst 是否“存在且不为空”，否则 fallback 用 1。TS/Java 里常写：burst != null && burst !== undefined ? burst : Math.max(1, Math.floor(rate))
        self._capacity = float(burst) if burst else max(1.0, float(rate))
 
        self._tokens = self._capacity
        self._last_refill = time.monotonic()
        # _lock 不是线程锁（threading.Lock），而是 asyncio 里的“协程间的异步锁”：
        # 保证 await acquire() 并发时，令牌桶的 _tokens 变量不会被多个协程同时修改，避免竞态。
        # 类比 TypeScript/JavaScript 里实现 async 互斥控制、C++ 里协程环境下的 co_mutex、Java 的异步锁机制。
        # 注意：asyncio.Lock 只保护同一个事件循环下的并发，对多线程无效（进程/线程安全另需其它方案）。
        self._lock = asyncio.Lock()

    # @classmethod 是 Python 的“类方法修饰器”：让下面的方法第一个参数变为类本身（cls），而不是实例（self）；
    # 这样可以用 TokenBucket.from_config(...) 直接通过类调用，常用于工厂方法或根据配置创建实例。
    # 类比 TypeScript static 方法、Java/C++ static/factory method，只是 Python 用装饰器语法明示。
    @classmethod
    def from_config(cls, config: RateLimitConfig) -> TokenBucket:
        return cls(rate=config.rate, burst=config.burst)

    # @property 是 Python 的属性装饰器：
    # 让下面的方法可以像访问变量/字段一样访问（无需加括号）。
    # 类比 TypeScript 里的 get 访问器、Java 的 getter，或者 C++ 的属性包装器。
    # 例如：bucket.rate（而不用 bucket.rate()），便于只读/只写控制和 API 直观性。
    @property
    def rate(self) -> float:
        return self._rate

    @property
    def burst(self) -> int:
        return int(self._capacity)

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        if elapsed <= 0:
            return
        self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
        self._last_refill = now


    async def acquire(self, tokens: float = 1.0) -> None:
        """消耗 tokens；不足时挂起等待，直到补充够为止。"""
        if tokens <= 0:
            raise ValueError("tokens 必须 > 0")
        async with self._lock:
            while True:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                needed = tokens - self._tokens
                await asyncio.sleep(needed / self._rate)
