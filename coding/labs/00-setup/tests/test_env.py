import os

import pytest
from dotenv import load_dotenv


def test_import_openai():
    import openai  # noqa: F401


def test_import_pydantic():
    from pydantic import BaseModel  # noqa: F401


def test_dotenv_loads():
    load_dotenv()
    # 国内学习默认检查 DeepSeek；OpenAI Key 可选
    _ = os.getenv("DEEPSEEK_API_KEY", "")
    _ = os.getenv("OPENAI_API_KEY", "")
