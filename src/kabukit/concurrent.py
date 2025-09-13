from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable, Iterable


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
