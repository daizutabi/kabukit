from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import polars as pl
from polars import DataFrame

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable, Iterable


# async def fetch[T](
#     function: Callable[[T], Awaitable[DataFrame]],
#     iterable: Iterable[T],
#     /,
#     max_concurrency: int = 24,
#     *,
#     bar: bool = False,
#     total: int | None = None,
# ) -> DataFrame:
#     """Fetch data concurrently using the provided function."""
#     if total is None:
#         iterable = list(iterable)
#         total = len(iterable)

#     ait = collect_async(function, iterable, max_concurrency=max_concurrency)

#     # if bar:
#     #     from marimo._plugins.stateless.status._progress import progress_bar

#     #     ait = progress_bar(ait, total=total)

#     dfs = [df async for df in ait if not df.is_empty()]

#     if dfs:
#         return pl.concat(dfs)

#     return DataFrame()


async def collect[R](
    awaitables: Iterable[Awaitable[R]],
    /,
    max_concurrency: int = 24,
) -> AsyncIterator[R]:
    semaphore = asyncio.Semaphore(max_concurrency)

    async def run(awaitable: Awaitable[R]) -> R:
        async with semaphore:
            return await awaitable

    futures = (run(awaitable) for awaitable in awaitables)

    async for future in asyncio.as_completed(futures):
        yield await future


async def collect_fn[T, R](
    function: Callable[[T], Awaitable[R]],
    args: Iterable[T],
    /,
    max_concurrency: int = 24,
) -> AsyncIterator[R]:
    awaitables = (function(arg) for arg in args)

    async for item in collect(awaitables, max_concurrency=max_concurrency):
        yield item
