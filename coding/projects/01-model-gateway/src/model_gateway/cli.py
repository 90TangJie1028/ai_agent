# 如果你在查看代码时遇到 “import 'typer' could not be resolved” 的提示，
# 说明你的 Python 环境（通常是 .venv 虚拟环境）没有安装 typer。
# 推荐在项目根目录下的 .venv 虚拟环境中安装依赖包（这样不会影响全局 Python 环境）。
# 安装方法如下（假设你已在项目目录下且 .venv 已创建并激活）：
#   pip install typer
# 如果还没有创建虚拟环境，可以先运行：
#   python -m venv .venv
#   source .venv/bin/activate  (Linux/macOS)
#   .venv\Scripts\activate     (Windows)
# 然后再安装 typer：
#   pip install typer

# 这个模块用于定义基于 Typer 包的命令行界面（CLI），
# 提供通过命令行便捷调用 Model Gateway 各类功能的方式。
from pathlib import Path

import typer  # noqa

from model_gateway.bench import format_summary_table, run_bench
from model_gateway.gateway import ModelGateway

app = typer.Typer(help="P1 Model Gateway CLI — 默认 DeepSeek")


# 这个装饰器将下面的函数注册为 CLI 的一个子命令，
# 当用户运行 `python -m model_gateway.cli chat` 时，会调用这个函数。
@app.command()
def chat(
    message: str,
    provider: str | None = typer.Option(None, help="deepseek / moonshot / dashscope / openai"),
    model: str | None = typer.Option(None, help="覆盖默认模型名"),
):
    """发送一条 chat 消息。"""
    gateway = ModelGateway()
    gw = gateway.chat(message, provider=provider, model=model)
    record = gw.record
    if gw.result is None:
        typer.echo(f"调用失败: {record.error_type}", err=True)
        raise typer.Exit(code=1)
    result = gw.result
    typer.echo(result.content)
    typer.echo(
        f"\n[{result.provider}/{result.model}] "
        f"tokens={result.total_tokens} "
        f"(prompt={result.prompt_tokens}, completion={result.completion_tokens}) "
        f"latency={result.latency_ms}ms cost=${record.cost_usd:.6f}",
        err=True,
    )


@app.command()
def providers():
    """列出当前 .env 中已配置的 provider。"""
    gateway = ModelGateway()
    if not gateway.available_providers:
        typer.echo("未配置任何 API Key，请复制 .env.example → .env 并填入 DEEPSEEK_API_KEY")
        raise typer.Exit(code=1)
    for name in gateway.available_providers:
        typer.echo(name)


@app.command()
def bench(
    n: int = typer.Option(20, "--n", help="调用次数"),
    provider: str | None = typer.Option(
        "mock",
        help="provider 名；默认 mock 离线跑，不烧 API",
    ),
    model: str | None = typer.Option(None, help="覆盖默认模型名"),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="JSON 报告路径，默认 reports/week01-bench.json",
    ),
    use_async: bool = typer.Option(
        False,
        "--async",
        help="走 async_chat_batch（限流+并发）",
    ),
):
    """批量调用 N 次，汇总 token/费用/延迟，输出表格与 JSON 报告。"""
    try:
        report, out_path = run_bench(
            n,
            provider=provider,
            model=model,
            output=output,
            use_async=use_async,
        )
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(format_summary_table(report.summary))
    typer.echo(f"\n报告已写入: {out_path}", err=True)

    failures = [r for r in report.records if not r["success"]]
    if failures:
        typer.echo(f"\n失败 {len(failures)} 次:", err=True)
        for row in failures:
            typer.echo(
                f"  - {row['provider']}/{row['model']}: {row['error_type']}",
                err=True,
            )


if __name__ == "__main__":
    app()
