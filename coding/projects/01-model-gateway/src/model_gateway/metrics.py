"""调用指标：CallRecord、GatewayResult、MetricsCollector。"""

from __future__ import annotations

import statistics
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from model_gateway.adapters.base import ChatResult

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_PRICING_PATH = _PROJECT_ROOT / "config" / "pricing.yaml"

# 内置兜底，pricing.yaml 缺失时仍可按 default 计价
_BUILTIN_PRICING: dict[str, Any] = {
    "default": {"input_per_million": 1.0, "output_per_million": 2.0},
    "models": {
        "deepseek-chat": {"input_per_million": 0.14, "output_per_million": 0.28},
    },
}


def _parse_simple_pricing(text: str) -> dict[str, Any]:
    """解析本项目 pricing.yaml 的扁平结构，避免额外依赖。"""
    result: dict[str, Any] = {"default": {}, "models": {}}
    section: str | None = None
    current_model: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line == "default:":
            section = "default"
            current_model = None
            continue
        if line == "models:":
            section = "models"
            current_model = None
            continue
        if line.endswith(":") and section == "models":
            current_model = line[:-1].strip()
            result["models"][current_model] = {}
            continue
        if ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        try:
            parsed: int | float = float(value) if "." in value else int(value)
        except ValueError:
            parsed = value
        if section == "default":
            result["default"][key] = parsed
        elif section == "models" and current_model:
            result["models"][current_model][key] = parsed
    return result


def load_pricing(path: Path | None = None) -> dict[str, Any]:
    """加载 pricing 表；文件不存在时返回内置兜底。"""
    pricing_path = path or _DEFAULT_PRICING_PATH
    if not pricing_path.is_file():
        return _BUILTIN_PRICING
    return _parse_simple_pricing(pricing_path.read_text(encoding="utf-8"))


def compute_cost_usd(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    *,
    pricing: dict[str, Any] | None = None,
) -> float:
    """按 model 查单价，折算 USD。"""
    table = pricing or load_pricing()
    models = table.get("models", {})
    rates = models.get(model) or table.get("default", {})
    input_rate = float(rates.get("input_per_million", 0.0))
    output_rate = float(rates.get("output_per_million", 0.0))
    return (prompt_tokens * input_rate + completion_tokens * output_rate) / 1_000_000


@dataclass
class CallRecord:
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: int
    cost_usd: float
    success: bool
    error_type: str | None = None
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def from_chat_result(
        cls,
        chat: ChatResult,
        *,
        pricing: dict[str, Any] | None = None,
    ) -> CallRecord:
        return cls(
            provider=chat.provider,
            model=chat.model,
            prompt_tokens=chat.prompt_tokens,
            completion_tokens=chat.completion_tokens,
            total_tokens=chat.total_tokens,
            latency_ms=chat.latency_ms,
            cost_usd=compute_cost_usd(
                chat.model,
                chat.prompt_tokens,
                chat.completion_tokens,
                pricing=pricing,
            ),
            success=True,
            error_type=None,
        )

    @classmethod
    def from_error(
        cls,
        *,
        provider: str,
        model: str,
        exc: BaseException,
        latency_ms: int = 0,
    ) -> CallRecord:
        return cls(
            provider=provider,
            model=model,
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            latency_ms=latency_ms,
            cost_usd=0.0,
            success=False,
            error_type=type(exc).__name__,
        )


@dataclass
class GatewayResult:
    result: ChatResult | None
    record: CallRecord


@dataclass
class MetricsCollector:
    """内存聚合；bench 结束时 summary() / dump。"""

    # default_factory=list：避免 dataclass 可变默认值陷阱（多实例共用同一 list）
    records: list[CallRecord] = field(default_factory=list)

    def add(self, record: CallRecord) -> None:
        self.records.append(record)

    def summary(self) -> dict[str, float | int]:
        total = len(self.records)
        if total == 0:
            return {
                "count": 0,
                "success_count": 0,
                "success_rate": 0.0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "p95_latency_ms": 0,
            }
        # 筛选出 success 的 record
        successes = [r for r in self.records if r.success]
        # 排序 latency_ms
        latencies = sorted(r.latency_ms for r in successes)
        if latencies:
            p95_index = max(0, int(len(latencies) * 0.95) - 1)
            p95 = latencies[p95_index]
        else:
            p95 = 0

        return {
            "count": total,
            "success_count": len(successes),
            "success_rate": len(successes) / total,
            "total_tokens": sum(r.total_tokens for r in self.records),
            "total_cost_usd": sum(r.cost_usd for r in self.records),
            "p95_latency_ms": p95,
            "mean_latency_ms": int(statistics.mean(latencies)) if latencies else 0,
        }
