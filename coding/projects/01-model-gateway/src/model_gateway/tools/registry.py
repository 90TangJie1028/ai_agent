"""ToolRegistry：工具目录 + OpenAI/DeepSeek tools 导出 + 参数校验。

D10 只做「注册 / Schema / validate」。真正调模型、跑 handler 是 D11。

典型用法
--------
    registry = ToolRegistry()
    registry.register(
        name="calculator",
        description="Evaluate a basic arithmetic expression.",
        args_model=CalcArgs,
        handler=lambda args: str(eval_safe(args.expression)),  # D11 再用
    )
    tools_param = registry.to_openai_tools()   # 塞进 chat.completions.create(tools=...)
    args = registry.validate_args("calculator", '{"expression":"1+2"}')
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError


@dataclass(frozen=True, slots=True)
class ToolSpec:
    """单个工具的本地描述。"""

    name: str
    description: str
    args_model: type[BaseModel]
    # 执行函数：入参已是校验后的 Pydantic 模型；返回值转成 str 给 role=tool
    handler: Callable[[BaseModel], Any] | None = None


class ToolRegistry:
    """按名字管理工具；负责生成 API tools 列表与校验模型参数。"""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(
        self,
        name: str,
        description: str,
        args_model: type[BaseModel],
        handler: Callable[[BaseModel], Any] | None = None,
        *,
        replace: bool = False,
    ) -> None:
        """注册一个工具。name 建议 snake_case，与 API function.name 一致。"""
        if not name or not name.strip():
            raise ValueError("tool name must be non-empty")
        if not description.strip():
            raise ValueError(f"tool {name!r}: description must be non-empty")
        if not replace and name in self._tools:
            raise ValueError(f"tool already registered: {name!r}")
        self._tools[name] = ToolSpec(
            name=name,
            description=description.strip(),
            args_model=args_model,
            handler=handler,
        )

    def get(self, name: str) -> ToolSpec:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"unknown tool: {name!r}") from exc

    def names(self) -> list[str]:
        return sorted(self._tools)

    def to_openai_tools(self) -> list[dict[str, Any]]:
        """导出 chat.completions 请求体里的 tools= 参数。"""
        out: list[dict[str, Any]] = []
        for spec in self._tools.values():
            # parameters 用 Pydantic 的 JSON Schema；去掉 title 噪音可选，先保持完整
            parameters = spec.args_model.model_json_schema()
            out.append(
                {
                    "type": "function",
                    "function": {
                        "name": spec.name,
                        "description": spec.description,
                        "parameters": parameters,
                    },
                }
            )
        # 稳定顺序，方便测试快照
        out.sort(key=lambda item: item["function"]["name"])
        return out

    def validate_args(self, name: str, raw: str | dict[str, Any]) -> BaseModel:
        """校验模型给出的 tool arguments。

        - raw 可以是 JSON 字符串（API 常见）或已 parse 的 dict
        - 失败抛 pydantic.ValidationError（含 JSON 非法时包装成的错误）
        """
        spec = self.get(name)
        if isinstance(raw, str):
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                # 伪装成 ValidationError，调用方只需捕获一种异常
                raise ValidationError.from_exception_data(
                    title=spec.args_model.__name__,
                    line_errors=[
                        {
                            "type": "json_invalid",
                            "loc": (),
                            "input": raw,
                            "ctx": {"error": str(exc)},
                        }
                    ],
                ) from exc
        else:
            data = raw
        return spec.args_model.model_validate(data)

    def call(self, name: str, raw: str | dict[str, Any]) -> Any:
        """validate + 调 handler。D10 测试可用；D11 接到 gateway。"""
        spec = self.get(name)
        if spec.handler is None:
            raise RuntimeError(f"tool {name!r} has no handler")
        args = self.validate_args(name, raw)
        return spec.handler(args)
