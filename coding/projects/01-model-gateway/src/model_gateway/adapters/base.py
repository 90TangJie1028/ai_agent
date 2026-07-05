"""各厂商适配器共用接口。国内厂商多兼容 OpenAI Chat Completions 格式。"""

# 这行的意思是：从 Python 的 __future__ 模块导入 annotations 特性，使得在本文件中，
# 类型注解会以字符串的形式存储和处理（即 "延迟求值" 注解），
# 这样在类型注解中可以引用当前作用域下还未定义的类名、类型等，
# 提升代码的兼容性和灵活性。常用于需要提前引用还没定义的类/类型，或为支持新版 typing 语法做准备。
from __future__ import annotations

# 意思是导入 Python 的 dataclasses 模块中的 dataclass 装饰器，用于简化数据类的定义
# dataclass 是 Python 为简化数据类（即主要用于存储数据的类）定义而引入的一个装饰器。其作用是自动为类生成如 __init__、__repr__、__eq__ 等方法，减少样板代码。
# dataclasses 是包含 dataclass 装饰器以及相关工具函数（如 field、asdict 等）的标准库模块，专门用于数据类的创建和操作。
from dataclasses import dataclass
from typing import Any

# 意思是导入 Python 的 typing 模块中的 Protocol 类，用于定义协议（接口）
# Protocol 类用于定义结构化接口（协议类），允许指定实现类必须拥有哪些方法和属性，但不要求继承，实现“鸭子类型”。
from typing import Protocol


# @dataclass 是 Python 3.7+ 引入的装饰器，用于简化仅用于存储数据的类（数据类）的定义。
# 这些是 Python 类自动生成的一些魔术方法（如 __init__ 用于初始化对象，__repr__ 用于对象的字符串表示，__eq__ 用于判断对象是否相等等），主要是用来减少我们自己写样板代码的工作。@dataclass 装饰器可以自动帮我们生成这些常用方法，方便类的使用和属性管理。
@dataclass
# ChatResult 是用于封装一次聊天请求结果的数据类，记录模型回复内容、模型名、厂商名、Token 用量、延迟等信息。
class ChatResult:
    content: str                  # 回复内容
    model: str                    # 使用的模型名称
    provider: str                 # 提供者/厂商名称
    prompt_tokens: int = 0        # prompt 部分的 Token 数
    completion_tokens: int = 0    # completion 部分的 Token 数
    total_tokens: int = 0         # 总共消耗的 Token 数
    latency_ms: int = 0           # 延迟（毫秒）

# ChatAdapter 是聊天适配器的协议接口，定义所有适配器需实现的方法和属性
# 没错，这里的 Protocol 不是传入的参数，而是 Python typing 标准库里的一个基类，专门用来定义像接口一样的“协议类”。
# 这意思就类似 TypeScript 里的 interface，定义了一组约定，满足这些方法和属性签名的类都算符合 ChatAdapter 协议。
# Protocol 类型本身的作用，就是用来声明一组方法和属性的“接口”，实现了这些约定的类，都可以被认为“符合”这个协议，常用于类型检查和鸭子类型判断。
# 作用：让你可以定义一组方法和属性的“契约”，实现这个协议的类只要“满足约定的方法签名”即可，无需明确继承，实现结构化类型检查（鸭子类型）。
class ChatAdapter(Protocol):
    provider: str  # 适配器对应的提供者名称

    # 下面这个方法的意思是：所有实现了 ChatAdapter 协议的类都要有这个 chat 方法，类似 TypeScript 里的 interface 要求实现的函数
    def chat(
        self,
        message: str,
        *,
        model: str | None = None,
        timeout: float | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> ChatResult:
        """发送 message 给指定模型，返回 ChatResult 结果"""
        ...


# dataclass 装饰器的作用是自动为类生成如 __init__、__repr__、__eq__ 等方法，减少样板代码，方便属性管理。