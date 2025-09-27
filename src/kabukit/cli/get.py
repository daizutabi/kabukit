from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

import typer
from async_typer import AsyncTyper  # pyright: ignore[reportMissingTypeStubs]
from typer import Argument

if TYPE_CHECKING:
    from kabukit.core.base import Base

app = AsyncTyper(
    add_completion=False,
    help="J-Quantsからデータを取得します。",
)

Code = Annotated[
    str | None,
    Argument(help="銘柄コード。指定しない場合は全銘柄の情報を取得します。"),
]


@app.async_command()  # pyright: ignore[reportUnknownMemberType]
async def info(code: Code = None) -> None:
    """上場銘柄一覧を取得します。"""
    from kabukit.core.info import Info
    from kabukit.jquants.client import JQuantsClient

    async with JQuantsClient() as client:
        df = await client.get_info(code)

    typer.echo(df)

    if code is None:
        path = Info(df).write()
        typer.echo(f"全銘柄の情報を '{path}' に保存しました。")


async def _fetch(
    code: str | None,
    target: str,
    cls: type[Base],
    fetch_func_name: str,
    message: str,
    **kwargs: Any,
) -> None:
    """財務情報・株価情報を取得するための共通処理"""
    from kabukit.jquants.client import JQuantsClient

    if code is not None:
        async with JQuantsClient() as client:
            df = await getattr(client, fetch_func_name)(code)
        typer.echo(df)
        return

    import tqdm.asyncio

    from kabukit.jquants.concurrent import fetch_all

    df = await fetch_all(target, progress=tqdm.asyncio.tqdm, **kwargs)
    typer.echo(df)
    path = cls(df).write()
    typer.echo(f"全銘柄の{message}を '{path}' に保存しました。")


@app.async_command()  # pyright: ignore[reportUnknownMemberType]
async def statements(code: Code = None) -> None:
    """財務情報を取得します。"""
    from kabukit.core.statements import Statements

    await _fetch(
        code=code,
        target="statements",
        cls=Statements,
        fetch_func_name="get_statements",
        message="財務情報",
    )


@app.async_command()  # pyright: ignore[reportUnknownMemberType]
async def prices(code: Code = None) -> None:
    """株価を取得します。"""
    from kabukit.core.prices import Prices

    await _fetch(
        code=code,
        target="prices",
        cls=Prices,
        fetch_func_name="get_prices",
        message="株価情報",
        max_concurrency=8,
    )


@app.async_command(name="list")  # pyright: ignore[reportUnknownMemberType]
async def list_() -> None:
    """書類一覧を取得します。"""
    import tqdm.asyncio

    from kabukit.core.list import List
    from kabukit.edinet.concurrent import fetch_list

    df = await fetch_list(years=10, progress=tqdm.asyncio.tqdm)
    typer.echo(df)
    path = List(df).write()
    typer.echo(f"書類一覧を '{path}' に保存しました。")


@app.async_command(name="all")  # pyright: ignore[reportUnknownMemberType]
async def all_(code: Code = None) -> None:
    """上場銘柄一覧、財務情報、株価、書類一覧を連続して取得します。"""
    typer.echo("上場銘柄一覧を取得します。")
    await info(code)

    typer.echo("---")
    typer.echo("財務情報を取得します。")
    await statements(code)

    typer.echo("---")
    typer.echo("株価を取得します。")
    await prices(code)

    if code is None:
        typer.echo("---")
        typer.echo("書類一覧を取得します。")
        await list_()
