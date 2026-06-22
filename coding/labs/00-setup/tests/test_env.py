import os

import pytest
from dotenv import load_dotenv


def test_import_openai():
    import openai  # noqa: F401


def test_import_pydantic():
    from pydantic import BaseModel  # noqa: F401


def test_dotenv_loads():
    load_dotenv()
    # Key may be empty in CI; file load should not raise
    _ = os.getenv("OPENAI_API_KEY", "")
