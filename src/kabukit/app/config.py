from __future__ import annotations

from typing import Annotated

import typer
from typer import Argument, Typer

from kabukit.config import set_key

app = Typer(
    name="config",
    help="Configuration management commands.",
)


@app.command("set")
def set_(
    key: Annotated[str, Argument(help="The key to set (e.g., EDINET_API_KEY).")],
    value: Annotated[str, Argument(help="The value to associate with the key.")],
) -> None:
    """Sets a configuration key to a specific value."""
    set_key(key, value)
    typer.echo(f"Successfully set '{key}' to '{value}'")
