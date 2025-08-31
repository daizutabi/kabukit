"""kabukit CLI."""

from __future__ import annotations

import pprint
from typing import TYPE_CHECKING, Annotated

import typer
from httpx import HTTPStatusError
from typer import Argument, Exit, Option, Typer

from .jquants.client import JQuantsClient, Key

app = Typer(add_completion=False)


@app.command()
def auth(
    mailaddress: Annotated[str, Argument(help="J-Quants mail address.")],
    password: Annotated[str, Option(prompt=True, hide_input=True)],
) -> None:
    """Authenticate and save/refresh tokens."""
    client = JQuantsClient()

    try:
        client.auth(mailaddress, password)
    except HTTPStatusError as e:
        typer.echo(f"Authentication failed: {e}")
        raise typer.Exit(code=1) from None

    typer.echo(client.refresh_token)
    typer.echo(client.id_token)


@app.command()
def issues() -> None:
    """Get listed issues."""
    client = _create_client()
    if not client.id_token:
        print("Authentication required. Please run 'kabu auth' first.")
        raise typer.Exit(code=1)

    try:
        print("Fetching listed issues...")
        issues_data = client.get_listed_issues()
        print("Listed issues:")
        pprint.pprint(issues_data["issues"])
    except Exception as e:
        print(f"An error occurred: {e}")
        raise typer.Exit(code=1)


@app.command()
def hello() -> None:
    """Say hello."""
    typer.echo("Hello, this is kabukit CLI!")
