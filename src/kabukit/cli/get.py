from __future__ import annotations

from typing import Annotated, Any

import tqdm.asyncio
import typer
from async_typer import AsyncTyper
from typer import Argument, Option

# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false


class CustomTqdm(tqdm.asyncio.tqdm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("ncols", 80)
        super().__init__(*args, **kwargs)


app = AsyncTyper(
    add_completion=False,
    help="J-QuantsまたはEDINETからデータを取得します。",
)

Arg = Annotated[str | None, Argument(help="銘柄コード (4桁) または日付 (YYYYMMDD)。")]
Code = Annotated[str | None, Argument(help="銘柄コード (4桁)。")]
Date = Annotated[str | None, Argument(help="取得する日付 (YYYYMMDD)。")]
All = Annotated[bool, Option("--all", help="全銘柄を取得します。")]
First = Annotated[bool, Option("--first", help="最初の行のみ表示します。")]
Last = Annotated[bool, Option("--last", help="最後の行のみ表示します。")]
MaxItems = Annotated[
    int | None,
    Option(
        "--max-items",
        help="取得する銘柄数を制限します。全銘柄取得時にのみ有効です。",
    ),
]
Quiet = Annotated[
    bool,
    Option("--quiet", "-q", help="プログレスバーおよびメッセージを表示しません。"),
]


@app.async_command()
async def calendar(
    *,
    first: First = False,
    last: Last = False,
    quiet: Quiet = False,
) -> None:
    """営業日カレンダーを取得します。"""
    from kabukit.sources.jquants.batch import get_calendar

    from .utils import display_dataframe, write_cache

    df = await get_calendar()
    display_dataframe(df, first=first, last=last, quiet=quiet)

    if not first and not last:
        write_cache(df, "jquants", "calendar", "営業日カレンダー", quiet=quiet)


@app.async_command()
async def info(
    arg: Arg = None,
    *,
    first: First = False,
    last: Last = False,
    quiet: Quiet = False,
) -> None:
    """銘柄情報を取得します。"""
    from kabukit.sources.jquants.batch import get_info

    from .utils import display_dataframe, get_code_date, write_cache

    df = await get_info(*get_code_date(arg))
    display_dataframe(df, first=first, last=last, quiet=quiet)

    if not any([arg, first, last]):
        write_cache(df, "jquants", "info", "全銘柄の銘柄情報", quiet=quiet)


@app.async_command()
async def statements(
    arg: Arg = None,
    *,
    all_: All = False,
    max_items: MaxItems = None,
    first: First = False,
    last: Last = False,
    quiet: Quiet = False,
) -> None:
    """財務情報を取得します。"""
    from kabukit.sources.jquants.batch import get_statements
    from kabukit.utils.datetime import today

    from .utils import display_dataframe, get_code_date, write_cache

    if arg is None and not all_:
        arg = today(as_str=True)

    df = await get_statements(
        *get_code_date(arg),
        max_items=max_items,
        progress=None if arg or quiet else CustomTqdm,
    )
    display_dataframe(df, first=first, last=last, quiet=quiet)

    if not any([arg, max_items, first, last]):
        write_cache(df, "jquants", "statements", "全銘柄の財務情報", quiet=quiet)


@app.async_command()
async def prices(
    arg: Arg = None,
    *,
    all_: All = False,
    max_items: MaxItems = None,
    first: First = False,
    last: Last = False,
    quiet: Quiet = False,
) -> None:
    """株価情報を取得します。"""
    from kabukit.sources.jquants.batch import get_prices
    from kabukit.utils.datetime import today

    from .utils import display_dataframe, get_code_date, write_cache

    if arg is None and not all_:
        arg = today(as_str=True)

    df = await get_prices(
        *get_code_date(arg),
        max_items=max_items,
        progress=None if arg or quiet else CustomTqdm,
    )
    display_dataframe(df, first=first, last=last, quiet=quiet)

    if not any([arg, max_items, first, last]):
        write_cache(df, "jquants", "prices", "全銘柄の株価情報", quiet=quiet)


@app.async_command()
async def jquants(
    arg: Arg = None,
    *,
    all_: All = False,
    max_items: MaxItems = None,
    first: First = False,
    last: Last = False,
    quiet: Quiet = False,
) -> None:
    """J-Quants APIから全情報を取得します。"""
    typer.echo("- 銘柄情報を取得します。")
    await info(arg, first=first, last=last, quiet=quiet)

    typer.echo("- 財務情報を取得します。")
    await statements(
        arg,
        all_=all_,
        max_items=max_items,
        first=first,
        last=last,
        quiet=quiet,
    )

    typer.echo("- 株価情報を取得します。")
    await prices(
        arg,
        all_=all_,
        max_items=max_items,
        first=first,
        last=last,
        quiet=quiet,
    )


@app.async_command()
async def edinet(
    date: Date = None,
    *,
    all_: All = False,
    max_items: MaxItems = None,
    first: First = False,
    last: Last = False,
    quiet: Quiet = False,
) -> None:
    """EDINET APIから書類一覧を取得します。"""
    from kabukit.sources.edinet.batch import get_list
    from kabukit.utils.datetime import today

    from .utils import display_dataframe, get_code_date, write_cache

    if date is None and not all_:
        date = today(as_str=True)

    code, date_ = get_code_date(date)
    if code:
        typer.echo("銘柄コードではなく日付を指定してください。", err=True)
        raise typer.Exit(1)

    df = await get_list(
        date_,
        years=10,
        max_items=max_items,
        progress=None if date or quiet else CustomTqdm,
    )
    display_dataframe(df, first=first, last=last, quiet=quiet)

    if not any([date, max_items, first, last]):
        write_cache(df, "edinet", "list", "EDINET書類一覧", quiet=quiet)


@app.async_command()
async def tdnet(
    date: Date = None,
    *,
    all_: All = False,
    max_items: MaxItems = None,
    first: First = False,
    last: Last = False,
    quiet: Quiet = False,
) -> None:
    """TDnetから書類一覧を取得します。"""
    from kabukit.sources.tdnet.batch import get_list
    from kabukit.utils.datetime import today

    from .utils import display_dataframe, get_code_date, write_cache

    if date is None and not all_:
        date = today(as_str=True)

    code, date_ = get_code_date(date)
    if code:
        typer.echo("銘柄コードではなく日付を指定してください。", err=True)
        raise typer.Exit(1)

    df = await get_list(
        date_,
        max_items=max_items,
        progress=None if date or quiet else CustomTqdm,
    )
    display_dataframe(df, first=first, last=last, quiet=quiet)

    if not any([date, max_items, first, last]):
        write_cache(df, "tdnet", "list", "TDnet書類一覧", quiet=quiet)


@app.async_command()
async def yahoo(
    code: Code = None,
    *,
    all_: All = False,
    max_items: MaxItems = None,
    first: First = False,
    last: Last = False,
    quiet: Quiet = False,
) -> None:
    """Yahooファイナンスから情報を取得します。"""
    from kabukit.sources.yahoo.batch import get_quote

    from .utils import display_dataframe, write_cache

    if code is None and not all_:
        typer.echo("銘柄コードか --all オプションを指定してください。", err=True)
        raise typer.Exit(1)

    df = await get_quote(
        code,
        max_items=max_items,
        progress=None if code or quiet else CustomTqdm,
    )
    display_dataframe(df, first=first, last=last, quiet=quiet)

    if not any([code, max_items, first, last]):
        write_cache(df, "yahoo", "quote", "Yahooファイナンス銘柄情報", quiet=quiet)
