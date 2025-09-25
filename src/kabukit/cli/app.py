"""kabukit CLI."""

from __future__ import annotations

import typer
from async_typer import AsyncTyper  # pyright: ignore[reportMissingTypeStubs]

from . import auth, get

app = AsyncTyper(
    add_completion=False,
    help="J-Quants/EDINETデータツール",
)
app.add_typer(auth.app, name="auth")
app.add_typer(get.app, name="get")


@app.command()
def version() -> None:
    """バージョン情報を表示します。"""
    from importlib.metadata import version

    typer.echo(f"kabukit version: {version('kabukit')}")
