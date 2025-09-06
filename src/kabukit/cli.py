"""kabukit CLI."""

from __future__ import annotations

import os
from typing import Annotated

import typer
from httpx import HTTPStatusError
from typer import Argument, Exit, Option, Typer

app = Typer(
    add_completion=False,
    help="Kabukit: J-QuantsおよびEDINETから金融データを取得するためのCLIツール。",
)


@app.command()
def auth(
    mailaddress: Annotated[str, Argument(help="J-Quantsに登録したメールアドレス。")],
    password: Annotated[
        str,
        Option(prompt=True, hide_input=True, help="J-Quantsのパスワード。"),
    ],
) -> None:
    """J-Quants APIの認証を行い、トークンを設定ファイルに保存します。"""
    from .jquants.client import JQuantsClient

    client = JQuantsClient()

    try:
        client.auth(mailaddress, password)
    except HTTPStatusError as e:
        typer.echo(f"認証に失敗しました: {e}")
        raise Exit(1) from None

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
    """kabukitのバージョン情報を表示します。"""
    from importlib.metadata import version

    typer.echo(f"kabukit version: {version('kabukit')}")
