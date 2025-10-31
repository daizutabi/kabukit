from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import polars as pl

from kabukit.utils import gather

from .client import TdnetClient

if TYPE_CHECKING:
    from collections.abc import Iterable

    from kabukit.utils.gather import Callback, Progress


async def get_list(
    dates: Iterable[datetime.date | str] | datetime.date | str | None = None,
    /,
    max_items: int | None = None,
    max_concurrency: int | None = None,
    progress: Progress | None = None,
    callback: Callback | None = None,
) -> pl.DataFrame:
    """TDnetの文書一覧を取得する。

    Args:
        dates (Iterable[datetime.date | str] | datetime.date | str | None):
            取得対象の日付のリスト。None の場合は現在取得可能な日付リストから生成する。
        max_items (int | None, optional): 取得数の上限。
        max_concurrency (int | None, optional): 同時に実行するリクエストの最大数。
            指定しないときはデフォルト値が使用される。
        progress (Progress | None, optional): 進捗表示のための関数。
            tqdm, marimoなどのライブラリを使用できる。
            指定しないときは進捗表示は行われない。
        callback (Callback | None, optional): 各DataFrameに対して適用する
            コールバック関数。指定しないときはそのままのDataFrameが使用される。

    Returns:
        DataFrame:
            文書一覧を含む単一のDataFrame。
    """
    if isinstance(dates, (str, datetime.date)):
        async with TdnetClient() as client:
            return await client.get_list(dates)

    if dates is None:
        async with TdnetClient() as client:
            dates = await client.get_dates()

    df = await gather.get(
        TdnetClient,
        "list",
        dates,
        max_items=max_items,
        max_concurrency=max_concurrency,
        progress=progress,
        callback=callback,
    )

    if df.is_empty():
        return pl.DataFrame()

    return df.sort("Code", "Date")
