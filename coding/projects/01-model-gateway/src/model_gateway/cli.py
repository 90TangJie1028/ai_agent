import typer

from model_gateway.gateway import ModelGateway

app = typer.Typer(help="P1 Model Gateway CLI — 默认 DeepSeek")


@app.command()
def chat(
    message: str,
    provider: str | None = typer.Option(None, help="deepseek / moonshot / dashscope / openai"),
    model: str | None = typer.Option(None, help="覆盖默认模型名"),
):
    """发送一条 chat 消息。"""
    gateway = ModelGateway()
    result = gateway.chat(message, provider=provider, model=model)
    typer.echo(result.content)
    typer.echo(
        f"\n[{result.provider}/{result.model}] "
        f"tokens={result.total_tokens} "
        f"(prompt={result.prompt_tokens}, completion={result.completion_tokens})",
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
