from __future__ import annotations

from typing import Annotated

import typer
from async_typer import AsyncTyper  # pyright: ignore[reportMissingTypeStubs]
from typer import Argument, Exit

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


@app.async_command()  # pyright: ignore[reportUnknownMemberType]
async def statements(code: Code = None) -> None:
    """財務情報を取得します。"""
    from kabukit.core.statements import Statements
    from kabukit.jquants.client import JQuantsClient

    if code is not None:
        async with JQuantsClient() as client:
            df = await client.get_statements(code)
        typer.echo(df)
        raise Exit

    import tqdm.asyncio

    from kabukit.jquants.concurrent import fetch_all

    df = await fetch_all("statements", progress=tqdm.asyncio.tqdm)
    typer.echo(df)
    path = Statements(df).write()
    typer.echo(f"全銘柄の財務情報を '{path}' に保存しました。")


@app.async_command()  # pyright: ignore[reportUnknownMemberType]
async def prices(code: Code = None) -> None:
    """株価を取得します。"""
    from kabukit.core.prices import Prices
    from kabukit.jquants.client import JQuantsClient

    if code is not None:
        async with JQuantsClient() as client:
            df = await client.get_prices(code)
        typer.echo(df)
        raise Exit

    import tqdm.asyncio

    from kabukit.jquants.concurrent import fetch_all

    df = await fetch_all("prices", max_concurrency=8, progress=tqdm.asyncio.tqdm)
    typer.echo(df)
    path = Prices(df).write()
    typer.echo(f"全銘柄の株価情報を '{path}' に保存しました。")
