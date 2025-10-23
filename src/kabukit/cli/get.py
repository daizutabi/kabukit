from __future__ import annotations

from typing import Annotated

import typer
from async_typer import AsyncTyper
from typer import Argument, Option

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

Arg = Annotated[str | None, Argument(help="銘柄コード (4桁) あるいは日付 (YYYYMMDD)。")]
Date = Annotated[str | None, Argument(help="取得する日付 (YYYYMMDD)。")]
Quiet = Annotated[
    bool,
    Option("--quiet", "-q", help="プログレスバーおよびメッセージを表示しません。"),
]
All = Annotated[bool, Option("--all", "-a", help="全銘柄を対象にします。")]
MaxItems = Annotated[
    int | None,
    Option("--max-items", help="取得する銘柄数の上限。全銘柄取得時にのみ有効です。"),
]


@app.async_command()
async def calendar(*, quiet: Quiet = False) -> None:
    """営業日カレンダーを取得します。"""
    from kabukit.domain import cache
    from kabukit.sources.jquants.concurrent import get_calendar

    df = await get_calendar()
    path = cache.write("jquants", "calendar", df)

    if not quiet:
        typer.echo(df)
        typer.echo(f"営業日カレンダーを '{path}' に保存しました。")


@app.async_command()
async def info(arg: Arg = None, *, quiet: Quiet = False) -> None:
    """上場銘柄一覧を取得します。"""
    from kabukit.domain import cache
    from kabukit.sources.jquants.concurrent import get_info
    from kabukit.utils.params import get_code_date

    df = await get_info(*get_code_date(arg))

    if not quiet:
        typer.echo(df)

    if arg is None:
        path = cache.write("jquants", "info", df)
        if not quiet:
            typer.echo(f"全銘柄の情報を '{path}' に保存しました。")


@app.async_command()
async def statements(
    arg: Arg = None,
    *,
    quiet: Quiet = False,
    max_items: MaxItems = None,
) -> None:
    """財務情報を取得します。"""
    import tqdm.asyncio

    from kabukit.domain import cache
    from kabukit.sources.jquants.concurrent import get_statements
    from kabukit.utils.params import get_code_date

    progress = None if arg or quiet else tqdm.asyncio.tqdm
    df = await get_statements(
        *get_code_date(arg),
        max_items=max_items,
        progress=progress,
    )

    if not quiet:
        typer.echo(df)

    if arg is None:
        path = cache.write("jquants", "statements", df)
        if not quiet:
            typer.echo(f"全銘柄の財務情報を '{path}' に保存しました。")


@app.async_command()
async def prices(
    arg: Arg = None,
    *,
    quiet: Quiet = False,
    max_items: MaxItems = None,
) -> None:
    """株価情報を取得します。"""
    import tqdm.asyncio

    from kabukit.domain import cache
    from kabukit.sources.jquants.concurrent import get_prices
    from kabukit.utils.params import get_code_date

    progress = None if arg or quiet else tqdm.asyncio.tqdm
    df = await get_prices(*get_code_date(arg), max_items=max_items, progress=progress)

    if not quiet:
        typer.echo(df)

    if arg is None:
        path = cache.write("jquants", "prices", df)
        if not quiet:
            typer.echo(f"全銘柄の株価情報を '{path}' に保存しました。")


@app.async_command()
async def jquants(
    arg: Arg = None,
    *,
    quiet: Quiet = False,
    max_items: MaxItems = None,
) -> None:
    """J-Quants APIから全情報を取得します。"""
    typer.echo("上場銘柄一覧を取得します。")
    await info(arg, quiet=quiet)

    typer.echo("---")
    typer.echo("財務情報を取得します。")
    await statements(arg, quiet=quiet, max_items=max_items)

    typer.echo("---")
    typer.echo("株価情報を取得します。")
    await prices(arg, quiet=quiet, max_items=max_items)


@app.async_command()
async def edinet(
    date: Date = None,
    *,
    quiet: Quiet = False,
    max_items: MaxItems = None,
) -> None:
    """EDINET APIから書類一覧を取得します。"""
    import tqdm.asyncio

    from kabukit.domain import cache
    from kabukit.sources.edinet.concurrent import get_list
    from kabukit.utils.params import get_code_date

    _, date_ = get_code_date(date)

    progress = None if date or quiet else tqdm.asyncio.tqdm
    df = await get_list(date_, years=10, progress=progress, max_items=max_items)

    if not quiet:
        typer.echo(df)

    if not date:
        path = cache.write("edinet", "list", df)
        if not quiet:
            typer.echo(f"書類一覧を '{path}' に保存しました。")


@app.async_command()
async def tdnet(
    date: Date = None,
    *,
    quiet: Quiet = False,
    max_items: MaxItems = None,
) -> None:
    """TDnetから書類一覧を取得します。"""
    import tqdm.asyncio

    from kabukit.domain import cache
    from kabukit.sources.tdnet.concurrent import get_list
    from kabukit.utils.params import get_code_date

    _, date_ = get_code_date(date)

    progress = None if date or quiet else tqdm.asyncio.tqdm
    df = await get_list(date_, progress=progress, max_items=max_items)

    if not quiet:
        typer.echo(df)

    if not date:
        path = cache.write("tdnet", "list", df)
        if not quiet:
            typer.echo(f"書類一覧を '{path}' に保存しました。")
