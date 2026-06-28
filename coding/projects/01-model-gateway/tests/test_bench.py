"""bench：批量调用、聚合报告、故意失败路径。"""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from model_gateway.bench import (
    BENCH_FAIL_MARKER,
    build_bench_messages,
    run_bench,
)
from model_gateway.cli import app


def test_build_bench_messages_injects_two_failures():
    msgs = build_bench_messages(20)
    assert len(msgs) == 20
    assert msgs[-2] == ""
    assert msgs[-1] == BENCH_FAIL_MARKER
    assert msgs[0] == "bench ping 0"


def test_build_bench_messages_single_is_fail_marker():
    assert build_bench_messages(1) == [BENCH_FAIL_MARKER]


def test_run_bench_mock_n20(tmp_path: Path):
    out = tmp_path / "bench.json"
    report, path = run_bench(20, provider="mock", output=out)

    assert path == out
    assert report.meta["n"] == 20
    assert report.meta["provider"] == "mock"
    assert report.summary["count"] == 20
    assert report.summary["success_count"] == 18
    assert report.summary["success_rate"] == pytest.approx(0.9)
    assert report.summary["total_tokens"] > 0
    assert len(report.records) == 20

    failures = [r for r in report.records if not r["success"]]
    assert len(failures) == 2
    error_types = {r["error_type"] for r in failures}
    assert error_types == {"ValueError", "RuntimeError"}


def test_run_bench_mock_async(tmp_path: Path):
    out = tmp_path / "bench-async.json"
    report, _ = run_bench(5, provider="mock", output=out, use_async=True)
    assert report.meta["async"] is True
    assert report.summary["count"] == 5
    assert report.summary["success_count"] == 3


def test_bench_cli_mock(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["bench", "--n", "5", "--output", str(tmp_path / "cli.json")])
    assert result.exit_code == 0
    assert "success_rate" in result.stdout or "90.0%" in result.stdout
    assert (tmp_path / "cli.json").is_file()
