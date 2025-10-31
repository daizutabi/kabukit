from __future__ import annotations

from typing import TYPE_CHECKING

from kabukit.sources.jquants.batch import get_target_codes
from kabukit.utils import gather

from .client import YahooClient

if TYPE_CHECKING:
    from collections.abc import Iterable

    import polars as pl

    from kabukit.utils.gather import Callback, Progress


async def get_quote(
    codes: Iterable[str] | str | None = None,
    /,
    max_items: int | None = None,
    max_concurrency: int = 12,
    progress: Progress | None = None,
    callback: Callback | None = None,
) -> pl.DataFrame:
    """Yahooファイナンスから情報を取得する。

    Args:
        codes (Iterable[str] | str, optional): 財務情報を取得する銘柄のコード。
            省略された場合、全銘柄が対象となる。
        max_items (int | None, optional): 取得する銘柄数の上限。
            指定しないときはすべての銘柄が対象となる。
        max_concurrency (int | None, optional): 同時に実行するリクエストの最大数。
            デフォルト値12。
        progress (Progress | None, optional): 進捗表示のための関数。
            tqdm, marimoなどのライブラリを使用できる。
            指定しないときは進捗表示は行われない。
        callback (Callback | None, optional): 各DataFrameに対して適用する
            コールバック関数。指定しないときはそのままのDataFrameが使用される。

    Returns:
        pl.DataFrame: Yahooファイナンスの情報を含むDataFrame。

    Raises:
        HTTPStatusError: APIリクエストが失敗した場合。
    """
    if isinstance(codes, str):
        async with YahooClient() as client:
            return await client.get_quote(codes)

    if codes is None:
        codes = await get_target_codes()

    data = await gather.get(
        YahooClient,
        "quote",
        codes,
        max_items=max_items,
        max_concurrency=max_concurrency,
        progress=progress,
        callback=callback,
    )
    return data.sort("Code")
