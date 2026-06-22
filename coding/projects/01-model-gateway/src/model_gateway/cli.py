import typer

app = typer.Typer(help="P1 Model Gateway CLI")


@app.command()
def chat(message: str):
    """Send a chat message (TODO D2)."""
    typer.echo(f"TODO: chat with: {message}")


@app.command()
def bench(n: int = 20):
    """Run n benchmark calls (TODO D6)."""
    typer.echo(f"TODO: bench n={n}")


if __name__ == "__main__":
    app()
