"""从环境变量加载模型网关配置。"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    api_key: str
    base_url: str
    default_model: str


def _provider(
    name: str,
    key_env: str,
    url_env: str,
    model_env: str,
    default_model: str,
    default_url: str,
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
