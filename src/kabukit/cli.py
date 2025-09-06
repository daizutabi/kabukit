"""kabukit CLI."""

from __future__ import annotations

import os
from typing import Annotated

import typer
from httpx import HTTPStatusError
from typer import Argument, Exit, Option, Typer

app = Typer(add_completion=False)


@app.command()
def auth(
    mailaddress: Annotated[str, Argument(help="J-Quants mail address.")],
    password: Annotated[str, Option(prompt=True, hide_input=True)],
) -> None:
    """Authenticate and save/refresh tokens."""
    from .jquants.client import JQuantsClient

    client = JQuantsClient()

    try:
        client.auth(mailaddress, password)
    except HTTPStatusError as e:
        typer.echo(f"Authentication failed: {e}")
        raise Exit(1) from None

    client = JQuantsClient()

    if refresh_token := client.refresh_token:
        typer.echo(f"refreshToken: {refresh_token[:30]}...")
    if id_token := client.id_token:
        typer.echo(f"idToken: {id_token[:30]}...")


@app.command()
def edinet(api_key: Annotated[str, Option(prompt=True)]) -> None:
    """Set EDINET API key."""

    from .config import load_dotenv, set_key

    set_key("EDINET_API_KEY", api_key)

    load_dotenv()
    if os.getenv("EDINET_API_KEY") == api_key:
        typer.echo("EDINET_API_KEY has been set.")


@app.command()
def version() -> None:
    """Show kabukit version."""
    from importlib.metadata import version

    typer.echo(f"kabukit version: {version('kabukit')}")
