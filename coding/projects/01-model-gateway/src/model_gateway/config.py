"""从环境变量加载模型网关配置。"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# 这个 .env 文件通常用于存储敏感信息（如 API 密钥），避免硬编码在代码中，提高安全性。

# load_dotenv() 的作用是：从当前工作目录（通常是项目根目录）加载 .env 文件，
# 并将其中的环境变量设置为系统环境变量，这样可以在代码中通过 os.getenv() 获取这些变量。
# 这样做的目的是：让代码更容易部署和配置，尤其是在开发、测试、生产环境需要不同配置时。
# 比如：开发时在 .env 中配置 DEEPSEEK_API_KEY，而生产环境可能需要使用不同的 API 密钥。
load_dotenv()


# frozen=True 的作用是让 dataclass 实例变成不可变对象（immutable）：实例创建后，属性不能被修改或新增，类似于 namedtuple 或只读的对象。
# 好处：可哈希（可以作为字典的 key），更安全，防止意外修改，方便在多线程环境下使用。
# Python 特性解释：
# - @dataclass 是 Python 3.7+ 提供，用于减少样板代码，自动生成 __init__、__repr__、__eq__ 等方法。
# - frozen=True 会自动生成 __setattr__ 和 __delattr__，禁止对实例属性赋值或删除，若强行赋值会抛出 FrozenInstanceError。
# - 这种不可变数据结构可用于参数配置、元数据等场景。
# dataclass 还有许多属性（参数），比如：
# - init: 自动生成 __init__ 方法，默认 True。
# - repr: 自动生成 __repr__ 方法，默认 True。
# - eq: 自动生成 __eq__ 方法，默认 True。
# - order: 自动生成排序方法 (__lt__、__le__、__gt__、__ge__)，默认 False。
# - unsafe_hash: 如果为 True，即使 frozen=False 也会生成 __hash__，默认 False。
# - slots: Python 3.10+ 新特性，为 True 时使用 __slots__，可减少内存、禁止动态添加属性。

# frozen 类似于 JS 的 Object.defineProperty({writable: false})，都能实现“只读”属性效果。

# 可以这么理解，Python 的 @dataclass(frozen=True) 其实就是在 dataclass 帮你实现了一个“只读开关”，
# 通过重写 __setattr__ 和 __delattr__ 魔法方法，在你尝试修改属性时抛出异常，从而“禁止修改”——
# 本质上只是加了一层上层逻辑的拦截（类似一个 if 条件），而并不是像 C++ 的 const 一样底层内存彻底锁死了；
# JS 的 Object.defineProperty({writable: false}) 也是加了属性的标志，普通代码下不能改，
# 但底层实际上属性还是在那里（特殊手段可以绕过）。
# 所以两者都是通过更高层的“逻辑约束（布尔开关）”来达到不可变效果——而不是底层彻底锁定内存。
@dataclass(
    frozen=True,      # 实例不可变
    init=True,        # 自动 __init__ 构造
    repr=True,        # 自动 __repr__ 打印
    eq=True,          # 自动 __eq__ 比较
    order=False,      # 不生成排序
    unsafe_hash=False,# 不强制 __hash__
    slots=False       # 不启用 __slots__
)
# 你说得对，Python 没有 TypeScript 的 interface 或 C++ 的 struct 语法，数据对象通常用 class 来表示结构。
# 在 Python 里，如果你想定义 "只描述数据结构" 的对象，可以用 class + type hint（如下），
# 或者更现代的做法是用 @dataclass。
# 最简单的写法就是这样，仅声明属性和类型：
class ProviderConfig:
    name: str
    api_key: str
    base_url: str
    default_model: str


# 以下下划线开头的方法（如 _provider）在 Python 中表示这是“内部使用”或“私有”方法
# （convention: internal/private use）。Python 并不会真正限制其访问，
# 但这是对开发者的约定，提醒外部不要直接调用它，仅供模块或文件内部使用。
def _provider(
    name: str,           # 厂商名称（如 "deepseek"）
    key_env: str,        # 存放 API Key 的环境变量名（如 "DEEPSEEK_API_KEY"）
    url_env: str,        # 存放 base_url 的环境变量名（如 "DEEPSEEK_BASE_URL"）
    model_env: str,      # 存放默认模型名的环境变量（如 "DEFAULT_MODEL" 或 "MOONSHOT_MODEL"）
    default_model: str,  # 默认模型名称（如 "deepseek-chat"）
    default_url: str,    # 默认 base_url 地址（如 "https://api.deepseek.com/v1"）
) -> ProviderConfig | None:
    api_key = os.getenv(key_env, "").strip()
    if not api_key:
        return None
    return ProviderConfig(
        name=name,
        api_key=api_key,
        base_url=os.getenv(url_env, default_url).strip(),
        default_model=os.getenv(model_env, default_model).strip(),
    )


def get_default_provider() -> str:
    return os.getenv("DEFAULT_PROVIDER", "deepseek").strip().lower()


def get_default_model() -> str:
    return os.getenv("DEFAULT_MODEL", "deepseek-chat").strip()


def load_providers() -> dict[str, ProviderConfig]:
    """已配置 Key 的厂商；未配置 Key 的厂商不会出现在字典中。"""
    providers: dict[str, ProviderConfig] = {}

    deepseek = _provider(
        "deepseek",
        "DEEPSEEK_API_KEY",
        "DEEPSEEK_BASE_URL",
        "DEFAULT_MODEL",
        "deepseek-chat",
        "https://api.deepseek.com/v1",
    )
    if deepseek:
        providers["deepseek"] = deepseek

    moonshot = _provider(
        "moonshot",
        "MOONSHOT_API_KEY",
        "MOONSHOT_BASE_URL",
        "MOONSHOT_MODEL",
        "moonshot-v1-8k",
        "https://api.moonshot.cn/v1",
    )
    if moonshot:
        providers["moonshot"] = moonshot

    dashscope = _provider(
        "dashscope",
        "DASHSCOPE_API_KEY",
        "DASHSCOPE_BASE_URL",
        "DASHSCOPE_MODEL",
        "qwen-plus",
        "https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    if dashscope:
        providers["dashscope"] = dashscope

    openai = _provider(
        "openai",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_MODEL",
        "gpt-4o-mini",
        "https://api.openai.com/v1",
    )
    if openai:
        providers["openai"] = openai

    return providers
