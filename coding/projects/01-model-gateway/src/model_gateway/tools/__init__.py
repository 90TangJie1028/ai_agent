"""工具注册与 Schema 校验（Function Calling 本地侧）。"""

from model_gateway.tools.calculator import (
    CalcArgs,
    build_default_registry,
    eval_safe,
    register_calculator,
)
from model_gateway.tools.registry import ToolRegistry, ToolSpec

__all__ = [
    "CalcArgs",
    "ToolRegistry",
    "ToolSpec",
    "build_default_registry",
    "eval_safe",
    "register_calculator",
]
