"""kabukit CLI."""

from __future__ import annotations

import os
from typing import Annotated

import typer
from async_typer import AsyncTyper  # pyright: ignore[reportMissingTypeStubs]
from httpx import HTTPStatusError
from typer import Exit, Option

app = AsyncTyper(
    add_completion=False,
    help="J-QuantsおよびEDINETの認証トークンを保存する。",
)


@app.async_command()  # pyright: ignore[reportUnknownMemberType]
async def jquants(
    mailaddress: Annotated[
        str,
        Option(prompt=True, help="J-Quantsに登録したメールアドレス。"),
    ],
    password: Annotated[
        str,
        Option(prompt=True, hide_input=True, help="J-Quantsのパスワード。"),
    ],
) -> None:
    """J-Quants APIの認証を行い、トークンを設定ファイルに保存します。"""
    from .jquants.client import JQuantsClient

    client = JQuantsClient()

    try:
        await client.auth(mailaddress, password)
    except HTTPStatusError as e:
        typer.echo(f"認証に失敗しました: {e}")
        raise Exit(1) from None
    finally:
        await client.aclose()

    typer.echo("J-Quantsのリフレッシュトークン・IDトークンを保存しました。")


@app.command()
def edinet(
    api_key: Annotated[str, Option(prompt=True, help="取得したEDINET APIキー。")],
) -> None:
    """EDINET APIのAPIキーを設定ファイルに保存します。"""

    from .config import load_dotenv, set_key

    set_key("EDINET_API_KEY", api_key)

    load_dotenv()
    if os.getenv("EDINET_API_KEY") == api_key:
        typer.echo("EDINETのAPIキーを保存しました。")


@app.command()
def show() -> None:
    """設定ファイルに保存したトークン・APIキーを表示します。"""
    from dotenv import dotenv_values

    from .config import get_dotenv_path

    path = get_dotenv_path()
    typer.echo(f"Configuration file: {path}")

    if path.exists():
        config = dotenv_values(path)
        for key, value in config.items():
            typer.echo(f"{key}: {value}")


@app.command()
def version() -> None:
    """バージョン情報を表示します。"""
    from importlib.metadata import version

    typer.echo(f"kabukit version: {version('kabukit')}")
