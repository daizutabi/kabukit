from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import polars as pl
from polars import DataFrame

if TYPE_CHECKING:
    from collections.abc import (
        AsyncIterable,
        AsyncIterator,
        Awaitable,
        Callable,
        Iterable,
    )


async def fetch[T](
    function: Callable[[T], Awaitable[DataFrame]],
    iterable: Iterable[T],
    /,
    max_concurrency: int = 24,
    *,
    bar: bool = False,
    total: int | None = None,
) -> DataFrame:
    """Fetch data concurrently using the provided function."""
    if total is None:
        iterable = list(iterable)
        total = len(iterable)

    ait = async_map(function, iterable, max_concurrency=max_concurrency)

    if bar:
        ait = progress_bar(ait, total=total)

    dfs = [df async for df in ait if not df.is_empty()]

    if dfs:
        return pl.concat(dfs)

    return DataFrame()


async def async_map[T, R](
    function: Callable[[T], Awaitable[R]],
    args: Iterable[T],
    /,
    max_concurrency: int = 24,
) -> AsyncIterator[R]:
    """Execute an async function concurrently over an iterable.

    This function processes items concurrently using an asyncio event loop.
    It is designed for non-blocking I/O-bound tasks, such as web requests.

    Args:
        function: The async function to apply to each item in `args`.
        args: An iterable of arguments to be passed to `function`.
        max_concurrency: The maximum number of concurrent tasks, controlled by
            an `asyncio.Semaphore`.

    Yields:
        The results of applying `function` to each item, in the order
        they are completed.
    """
    semaphore = asyncio.Semaphore(max_concurrency)

    async def run(arg: T) -> R:
        async with semaphore:
            return await function(arg)

    async for future in asyncio.as_completed(run(arg) for arg in args):
        yield await future


async def progress_bar[T](
    ait: AsyncIterable[T],
    *,
    total: int,
    title: str | None = None,
    subtitle: str | None = None,
    completion_title: str | None = None,
    completion_subtitle: str | None = None,
    show_rate: bool = True,
    show_eta: bool = True,
    remove_on_exit: bool = False,
    disabled: bool = False,
) -> AsyncIterator[T]:
    """Wrap an async iterable with a progress bar.

    This function wraps an asynchronous iterable and displays a progress bar
    using marimo. It is useful for tracking the progress of long-running
    asynchronous operations.

    Args:
        ait: An asynchronous iterable to be wrapped.
        total: The total number of items in the iterable.
        title (str, optional): Optional title.
        subtitle (str, optional): Optional subtitle.
        completion_title (str, optional): Optional title to show during completion.
        completion_subtitle (str, optional): Optional subtitle to show during
            completion.
        show_rate (bool, optional): If True, show the rate of progress
            (items per second).
        show_eta (bool, optional): If True, show the estimated time of completion.
        remove_on_exit (bool, optional): If True, remove the progress bar from
            output on exit.
        disabled (bool, optional): If True, disable the progress bar.

    Yields:
        Items from the original asynchronous iterable, while updating
        the progress bar.
    """
    from marimo._plugins.stateless.status._progress import progress_bar

    with progress_bar(
        total=total,
        title=title,
        subtitle=subtitle,
        completion_title=completion_title,
        completion_subtitle=completion_subtitle,
        show_rate=show_rate,
        show_eta=show_eta,
        remove_on_exit=remove_on_exit,
        disabled=disabled,
    ) as bar:
        async for item in ait:
            yield item
            bar.update()
