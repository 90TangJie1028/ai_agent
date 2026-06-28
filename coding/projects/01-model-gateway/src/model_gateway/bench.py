"""bench：批量调用 Gateway，MetricsCollector 聚合，输出报告。"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass

from pathlib import Path
from typing import Any

from model_gateway.config import get_default_provider
from model_gateway.gateway import ModelGateway
from model_gateway.metrics import CallRecord, MetricsCollector

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_REPORT_PATH = _PROJECT_ROOT / "reports" / "week01-bench.json"

# MockAdapter 识别此消息并抛错，用于 bench 故意失败路径
BENCH_FAIL_MARKER = "__bench_fail__"
BENCH_INVALID_MODEL = "__bench_invalid_model__"


@dataclass
class BenchCall:
    message: str
    timeout: float | None = None
    model: str | None = None


def build_bench_calls(n: int, *, provider: str = "mock") -> list[BenchCall]:
    """生成 n 次调用；最后 2 次为故意错误场景。"""
    if n <= 0:
        return []
    calls = [BenchCall(message=f"bench ping {i}") for i in range(n)]
    if n >= 2:
        calls[-2] = BenchCall(message="")
        if provider == "mock":
            calls[-1] = BenchCall(message=BENCH_FAIL_MARKER)
        else:
            calls[-1] = BenchCall(message=f"bench ping {n - 1}", model=BENCH_INVALID_MODEL)
    elif provider == "mock":
        calls[0] = BenchCall(message=BENCH_FAIL_MARKER)
    else:
        calls[0] = BenchCall(message="", model=BENCH_INVALID_MODEL)
    return calls


def build_bench_messages(n: int, *, provider: str = "mock") -> list[str]:
    """兼容旧接口；仅返回 message 列表。"""
    return [call.message for call in build_bench_calls(n, provider=provider)]


def call_record_to_dict(record: CallRecord) -> dict[str, Any]:
    return {
        "provider": record.provider,
        "model": record.model,
        "prompt_tokens": record.prompt_tokens,
        "completion_tokens": record.completion_tokens,
        "total_tokens": record.total_tokens,
        "latency_ms": record.latency_ms,
        "cost_usd": record.cost_usd,
        "success": record.success,
        "error_type": record.error_type,
        "timestamp": record.timestamp,
    }


@dataclass
class BenchReport:
    meta: dict[str, Any]
    summary: dict[str, float | int]
    records: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "meta": self.meta,
            "summary": self.summary,
            "records": self.records,
        }


def run_bench_sync(
    gateway: ModelGateway,
    calls: list[BenchCall],
    *,
    provider: str | None = None,
    model: str | None = None,
) -> MetricsCollector:
    collector = MetricsCollector()
    for call in calls:
        gw = gateway.chat(
            call.message,
            provider=provider,
            model=call.model or model,
            timeout=call.timeout,
        )
        collector.add(gw.record)
    return collector


async def run_bench_async(
    gateway: ModelGateway,
    calls: list[BenchCall],
    *,
    provider: str | None = None,
    model: str | None = None,
) -> MetricsCollector:
    collector = MetricsCollector()
    for call in calls:
        gw = await gateway.async_chat(
            call.message,
            provider=provider,
            model=call.model or model,
            timeout=call.timeout,
        )
        collector.add(gw.record)
    return collector


def build_bench_report(
    collector: MetricsCollector,
    *,
    n: int,
    provider: str,
    model: str,
    elapsed_sec: float,
    async_mode: bool = False,
) -> BenchReport:
    return BenchReport(
        meta={
            "timestamp": time.time(),
            "n": n,
            "provider": provider,
            "model": model,
            "elapsed_sec": round(elapsed_sec, 3),
            "async": async_mode,
        },
        summary=collector.summary(),
        records=[call_record_to_dict(r) for r in collector.records],
    )


def format_summary_table(summary: dict[str, float | int]) -> str:
    rate = float(summary["success_rate"]) * 100
    lines = [
        "=== Bench Summary ===",
        f"count             {summary['count']}",
        f"success_count     {summary['success_count']}",
        f"success_rate      {rate:.1f}%",
        f"total_tokens      {summary['total_tokens']}",
        f"total_cost_usd    ${float(summary['total_cost_usd']):.6f}",
        f"mean_latency_ms   {summary.get('mean_latency_ms', 0)}",
        f"p95_latency_ms    {summary['p95_latency_ms']}",
    ]
    return "\n".join(lines)


def write_bench_report(report: BenchReport, path: Path | None = None) -> Path:
    out = path or _DEFAULT_REPORT_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out


def run_bench(
    n: int = 20,
    *,
    provider: str | None = None,
    model: str | None = None,
    output: Path | None = None,
    use_async: bool = False,
) -> tuple[BenchReport, Path]:
    """执行 bench 全流程：构造消息 → 批量 chat → 聚合 → 写 JSON。"""
    gateway = ModelGateway(provider=provider)
    resolved_provider = (provider or get_default_provider()).lower()
    if resolved_provider not in gateway.available_providers:
        configured = ", ".join(gateway.available_providers) or "无"
        raise ValueError(
            f"未配置 provider={resolved_provider!r}。请在 .env 填入对应 API Key。"
            f" 当前可用: {configured}"
        )
    calls = build_bench_calls(n, provider=resolved_provider)
    if not calls:
        raise ValueError("n 必须大于 0")

    chat_provider = provider
    started = time.perf_counter()
    if use_async:
        collector = asyncio.run(
            run_bench_async(
                gateway,
                calls,
                provider=chat_provider,
                model=model,
            )
        )
    else:
        collector = run_bench_sync(
            gateway,
            calls,
            provider=chat_provider,
            model=model,
        )
    elapsed = time.perf_counter() - started

    sample = collector.records[0]
    report = build_bench_report(
        collector,
        n=n,
        provider=sample.provider,
        model=sample.model,
        elapsed_sec=elapsed,
        async_mode=use_async,
    )
    out_path = write_bench_report(report, output)
    return report, out_path
