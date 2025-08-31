"""kabukit CLI."""

from __future__ import annotations

import pprint

import typer

from .jquants.client import JQuantsClient

app = typer.Typer(add_completion=False)


def _create_client() -> JQuantsClient:
    refresh_token, email, password = load_jquants_auth_env()
    return JQuantsClient(refresh_token=refresh_token, email=email, password=password)


@app.command()
def issues() -> None:
    """Get listed issues."""
    try:
        client = _create_client()
        print("Authentication successful!")
        issues_data = client.get_listed_issues()
        print("Listed issues:")
        pprint.pprint(issues_data["issues"])
    except Exception as e:
        print(f"An error occurred: {e}")


@app.command()
def hello() -> None:
    """Say hello."""
    typer.echo("Hello, this is kabukit CLI!")
