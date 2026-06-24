"""重试与超时：指数退避、可重试异常判定。"""

from __future__ import annotations

import functools  # 用于实现重试装饰器
import time
from collections.abc import Callable  # retry 重试机制与超时控制模块
from dataclasses import dataclass
# typing.ParamSpec 和 typing.TypeVar 是 Python 3.10+ 中用于类型注解的泛型参数和返回值类型工具
from typing import ParamSpec, TypeVar

# openai 是用于与 OpenAI API 交互的 Python 客户端库
# APIConnectionError 表示连接 OpenAI API 时发生错误
# APIStatusError 表示 OpenAI API 返回的状态码错误
# APITimeoutError 表示 OpenAI API 请求超时
# RateLimitError 表示 OpenAI API 请求被限流
from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError

# ParamSpec 用于定义函数【参数】的类型，P 是 ParamSpec 的别名，类似 TypeScript 的 function 的泛型参数 func(k,v,...)
# 捕获「整份参数列表」
P = ParamSpec("P")
# TypeVar 用于定义函数【返回值】的类型，R 是 TypeVar 的别名，类似 TypeScript 的 <T>
# 捕获「返回值类型」
R = TypeVar("R")

# frozenset 是一种不可变集合（immutable set），用来存储一组[唯一]、[无序]的元素，并且创建后[不能修改]（不能添加或删除元素）。
# 通常用来做为查找表使用，因为查找效率很高。这里用于存放需要重试的 HTTP 状态码。
# 类似于 TypeScript 的 const enum，但更简洁。
RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})

# 重试策略接口
@dataclass(frozen=True)
class RetryPolicy:
    # 最大重试次数
    max_retries: int = 3
    # 基础延迟时间
    base_delay_sec: float = 0.5
    # 最大延迟时间
    max_delay_sec: float = 8.0

# 是否可以重试
def is_retryable(exc: BaseException) -> bool:
    """429 限流、5xx 服务端错误、连接失败可重试；4xx（除 429）不重试。"""
    # 限流和链接错误可以重试
    if isinstance(exc, (RateLimitError, APIConnectionError)):
        return True
    # 状态码是 RETRYABLE_STATUS_CODES 中的可以重试
    if isinstance(exc, APIStatusError):
        return exc.status_code in RETRYABLE_STATUS_CODES
    # 其他情况不重试
    return False

# 根据 [重试次数] 和 [重试策略] 计算延迟时间
def backoff_delay(attempt: int, policy: RetryPolicy) -> float:
    """attempt 从 0 起：0.5s → 1s → 2s → …，封顶 max_delay_sec。"""
    # 计算延迟时间，指数退避算法, [2,4,8,16,...] * base_delay_sec
    delay = policy.base_delay_sec * (2**attempt)
    # 返回延迟时间，但不超过最大延迟时间
    return min(delay, policy.max_delay_sec)

# with_ 开头函数 即 装饰器，用来包装某些函数，使其具有特定功能，比如重试、超时等。
# 这里 with_retry 
def with_retry(
    policy: RetryPolicy | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """装饰器：对可重试异常做指数退避；超时立即转 TimeoutError，不重试。"""

    retry_policy = policy or RetryPolicy()

    # 定义装饰器
    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        # @functools.wraps(fn) 是 Python 的装饰器，作用是让 wrapper 保留原函数 fn 的名字、文档、类型签名等属性。
        # 这样用 help() 或调试时看到的是被装饰函数的原始信息（比如函数名和文档），而不是 wrapper。
        # 类比 TypeScript 的装饰器“透传”原函数元数据，或者 C++/Java 注解里的 @Override；但 Python 运行期会实际复制 __name__、__doc__，TS 装饰器不会自动这样做。
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # 这里的 *args 和 **kwargs 不是“指针”，而是 Python 用于“可变参数列表”的语法——
        # *args：接受任意数量的“位置参数”，等价于 TypeScript/C++ 里的 ...args 或 Java 的 Object... args（可变长参数）。
        # **kwargs：接受任意数量的“关键字参数”，本质是个 dict；TypeScript 里可类比 Record<string, any>。
        # P.args, P.kwargs 是 typing.ParamSpec 泛型语法，用于类型安全地转发参数（TypeScript 可以类比 F extends (...args)=>any 的参数类型提取）。
        # 总结：*args/**kwargs ≈ 多语言的可变参数/参数转发
            last_exc: BaseException | None = None
            for attempt in range(retry_policy.max_retries + 1):
                try:
                    return fn(*args, **kwargs)
                # except 关键字用于捕获 try 代码块中抛出的指定类型异常，使程序进入 except 分支而不直接中止。
                # 这里 except APITimeoutError as exc: 的作用是“如果 fn(*args, **kwargs) 抛出了 APITimeoutError，
                # 就用 exc 变量接住它，转而执行该 except 块的代码”。类似 TypeScript/Java/C++ 的 try/catch (catch (exc))。
                except APITimeoutError as exc:
                    # 这里 raise TimeoutError(str(exc)) 的作用是“抛出一个 TimeoutError 异常，并把原始 APITimeoutError 作为原因”。
                    # 类似 TypeScript/Java/C++ 的 throw new Error(message) with cause。
                    # from exc 是 Python 的异常链语法，把原始异常附在当前异常后面，方便调试时追溯。
                    # 类比 TypeScript/Java/C++ 的 throw new Error(message) with cause。
                    raise TimeoutError(str(exc)) from exc
                except BaseException as exc:
                    if not is_retryable(exc) or attempt >= retry_policy.max_retries:
                        # 这里的 raise（不带参数）用来“原样重新抛出”刚才捕获到的异常，相当于 TypeScript/C++/Java 的 throw;（无参数），会把当前 except 捕获到的 exc 原封不动往上传递，不创建新异常。
                        raise
                    # 这里 last_exc = exc 的作用是“记录当前异常，用于后续 assert 检查”。
                    last_exc = exc
                    # 这里 time.sleep(backoff_delay(attempt, retry_policy)) 的作用是“根据重试次数和策略计算延迟，等待一段时间后重试”。
                    # 类似 TypeScript/Java/C++ 的 Thread.sleep(ms)。
                    time.sleep(backoff_delay(attempt, retry_policy))
            # 这里 assert last_exc is not None 的作用是“确保 last_exc 不为 None，否则抛出 AssertionError”。
            # 类似 TypeScript/Java/C++ 的 assert (condition)。
            assert last_exc is not None
            # 这里 raise last_exc 的作用是“最终抛出最后一次捕获的异常，结束重试循环”。
            # 类似 TypeScript/Java/C++ 的 throw last_exc;。
            raise last_exc

        return wrapper

    # 返回该装饰器
    return decorator
