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
import typer  # noqa

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
def bench(n: int = 20):
    """Run n benchmark calls (TODO D6)."""
    typer.echo(f"TODO: bench n={n} — 见 plan/weekly/week-01.md D6")


if __name__ == "__main__":
    app()
