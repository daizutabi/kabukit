from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

import typer
from async_typer import AsyncTyper
from typer import Argument, Option

if TYPE_CHECKING:
    from kabukit.core.base import Base

# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false


def set_table() -> None:
    import polars as pl

    pl.Config.set_tbl_rows(5)
    pl.Config.set_tbl_cols(6)
    pl.Config.set_tbl_hide_dtype_separator()


set_table()


app = AsyncTyper(
    add_completion=False,
    help="J-QuantsまたはEDINETからデータを取得します。",
)

Code = Annotated[
    str | None,
    Argument(help="銘柄コード。指定しない場合は全銘柄の情報を取得します。"),
]
Date = Annotated[
    str | None,
    Argument(help="取得する日付。指定しない場合は全期間の情報を取得します。"),
]
Quiet = Annotated[
    bool,
    Option("--quiet", "-q", help="プログレスバーを表示しません。"),
]


@app.async_command()
async def info(code: Code = None, *, quiet: Quiet = False) -> None:
    """上場銘柄一覧を取得します。"""
    from kabukit.core.info import Info
    from kabukit.jquants.client import JQuantsClient

    async with JQuantsClient() as client:
        df = await client.get_info(code)

    if code or not quiet:
        typer.echo(df)

    if code is None:
        path = Info(df).write()
        typer.echo(f"全銘柄の情報を '{path}' に保存しました。")


async def _get(
    code: str | None,
    target: str,
    cls: type[Base],
    method: str,
    message: str,
    *,
    quiet: bool = False,
    **kwargs: Any,
) -> None:
    """財務情報・株価情報を取得するための共通処理"""
    from kabukit.jquants.client import JQuantsClient

    if code is not None:
        async with JQuantsClient() as client:
            df = await getattr(client, method)(code)
        typer.echo(df)
        return

    import tqdm.asyncio

    from kabukit.jquants.concurrent import get

    progress = None if quiet else tqdm.asyncio.tqdm

    try:
        df = await get(target, progress=progress, **kwargs)
    except KeyboardInterrupt:
        typer.echo("中断しました。")
        raise typer.Exit(1) from None

    if not quiet:
        typer.echo(df)

    path = cls(df).write()
    typer.echo(f"全銘柄の{message}を '{path}' に保存しました。")


@app.async_command()
async def statements(code: Code = None, *, quiet: Quiet = False) -> None:
    """財務情報を取得します。"""
    from kabukit.core.statements import Statements

    await _get(
        code=code,
        target="statements",
        cls=Statements,
        method="get_statements",
        message="財務情報",
        quiet=quiet,
    )


@app.async_command()
async def prices(code: Code = None, *, quiet: Quiet = False) -> None:
    """株価情報を取得します。"""
    from kabukit.core.prices import Prices

    await _get(
        code=code,
        target="prices",
        cls=Prices,
        method="get_prices",
        message="株価情報",
        quiet=quiet,
        max_concurrency=8,
    )


@app.async_command()
async def entries(date: Date = None, *, quiet: Quiet = False) -> None:
    """書類一覧を取得します。"""
    import tqdm.asyncio

    from kabukit.core.entries import Entries
    from kabukit.edinet.concurrent import get_entries

    progress = None if date or quiet else tqdm.asyncio.tqdm

    try:
        df = await get_entries(date, years=10, progress=progress)
    except (KeyboardInterrupt, RuntimeError):
        typer.echo("中断しました。")
        raise typer.Exit(1) from None

    if not quiet:
        typer.echo(df)

    if not date:
        path = Entries(df).write()
        typer.echo(f"書類一覧を '{path}' に保存しました。")


@app.async_command(name="all")
async def all_(code: Code = None, *, quiet: Quiet = False) -> None:
    """上場銘柄一覧、財務情報、株価情報、書類一覧を連続して取得します。"""
    typer.echo("上場銘柄一覧を取得します。")
    await info(code, quiet=quiet)

    typer.echo("---")
    typer.echo("財務情報を取得します。")
    await statements(code, quiet=quiet)

    typer.echo("---")
    typer.echo("株価情報を取得します。")
    await prices(code, quiet=quiet)

    if code is None:
        typer.echo("---")
        typer.echo("書類一覧を取得します。")
        await entries(quiet=quiet)
