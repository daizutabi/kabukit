"""kabukit CLI."""

from __future__ import annotations

import pprint
from typing import TYPE_CHECKING, Annotated

import typer
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

    client.get_refresh_token(mailaddress, password)

    typer.echo(mailaddress)
    typer.echo(password)
    # try:
    #     if email and password:
    #         # Get and save a new refresh token
    #         print("Issuing a new refresh token...")
    #         refresh_token = client.get_refresh_token(email, password)
    #         client.save_token(Key.REFRESH_TOKEN, refresh_token)
    #         # Also get and save an ID token
    #         print("Issuing a new ID token...")
    #         id_token = client.get_id_token(refresh_token)
    #         client.save_token(Key.ID_TOKEN, id_token)
    #         print("\nAuthentication successful. Tokens are saved to .env file.")
    #     elif client.refresh_token:
    #         # Refresh and save the ID token using the existing refresh token
    #         print("Refreshing ID token...")
    #         id_token = client.get_id_token(client.refresh_token)
    #         client.save_token(Key.ID_TOKEN, id_token)
    #         print("ID token has been refreshed and saved.")
    #     else:
    #         print(
    #             "Error: No credentials or refresh token found. Please provide email/password\n"
    #             "or ensure JQUANTS_REFRESH_TOKEN is in your .env file.",
    #         )
    #         raise typer.Exit(code=1)
    # except Exception as e:
    #     print(f"An error occurred during authentication: {e}")
    #     raise typer.Exit(code=1)


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
