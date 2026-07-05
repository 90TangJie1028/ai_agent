"""D9 实验：同一 prompt，三种 structured 模式成功率对比。

运行（mock，无需 API Key）:
  PYTHONPATH=src python experiments/structured_vs_json.py

运行（真 API）:
  PYTHONPATH=src python experiments/structured_vs_json.py --provider deepseek -n 5
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

from model_gateway.gateway import ModelGateway
from model_gateway.structured_output import StructuredOutputMode


MODES: list[StructuredOutputMode] = ["prompt", "json_object", "json_schema"]
DEFAULT_PROMPT = "用一句话解释什么是递归，并给出置信度。"


@dataclass(frozen=True)
class ModeStats:
    mode: StructuredOutputMode
    attempts: int
    successes: int

    @property
    def rate(self) -> float:
        return self.successes / self.attempts if self.attempts else 0.0


def run_trial(
    gateway: ModelGateway,
    prompt: str,
    mode: StructuredOutputMode,
    *,
    provider: str | None,
    model: str | None,
) -> bool:
    gw = gateway.chat_structured(
        prompt,
        provider=provider,
        model=model,
        mode=mode,
    )
    return gw.result is not None and gw.record.success


def run_experiment(
    *,
    provider: str,
    model: str | None,
    prompt: str,
    attempts: int,
) -> list[ModeStats]:
    gateway = ModelGateway(provider=provider)
    results: list[ModeStats] = []
    for mode in MODES:
        ok = sum(
            1
            for _ in range(attempts)
            if run_trial(gateway, prompt, mode, provider=provider, model=model)
        )
        results.append(ModeStats(mode=mode, attempts=attempts, successes=ok))
    return results


def print_table(stats: list[ModeStats], *, provider: str, prompt: str) -> None:
    print(f"provider={provider!r}  prompt={prompt[:40]!r}...")
    print(f"{'mode':<14} {'success':>8} {'attempts':>8} {'rate':>8}")
    print("-" * 42)
    for row in stats:
        print(
            f"{row.mode:<14} {row.successes:>8} {row.attempts:>8} {row.rate:>7.0%}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="structured output mode comparison")
    parser.add_argument("--provider", default="mock", help="provider name (default: mock)")
    parser.add_argument("--model", default=None, help="model override")
    parser.add_argument("-n", "--attempts", type=int, default=3, help="trials per mode")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="user prompt")
    args = parser.parse_args(argv)

    stats = run_experiment(
        provider=args.provider,
        model=args.model,
        prompt=args.prompt,
        attempts=args.attempts,
    )
    print_table(stats, provider=args.provider, prompt=args.prompt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
