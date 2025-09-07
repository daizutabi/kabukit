from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import polars as pl
from polars import DataFrame

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterable


async def fetch[T](
    function: Callable[[T], Awaitable[DataFrame]],
    iterable: Iterable[T],
    /,
    max_concurrency: int = 24,
) -> DataFrame:
    """Fetch data concurrently using the provided function."""
    semaphore = asyncio.Semaphore(max_concurrency)

    async def fetch_single(arg: T) -> DataFrame:
        async with semaphore:
            try:
                return await function(arg)
            except Exception:  # noqa: BLE001
                return DataFrame()

    tasks = [fetch_single(arg) for arg in iterable]
    dfs = await asyncio.gather(*tasks)
    dfs = [df for df in dfs if not df.is_empty()]

    if dfs:
        return pl.concat(dfs)

    return DataFrame()
