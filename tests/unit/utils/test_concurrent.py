from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import polars as pl
import pytest

from kabukit.sources.base import Client

if TYPE_CHECKING:
    from collections.abc import AsyncIterable, AsyncIterator

pytestmark = pytest.mark.unit


async def sleep(seconds: list[float]):
    x = (asyncio.sleep(s, s) for s in seconds)
    y = asyncio.as_completed(x)
    for i in y:  # async for (python 3.13+)
        yield await i


@pytest.mark.asyncio
async def test_sleep() -> None:
    ait = sleep([0.03, 0.02, 0.01])
    result = [s async for s in ait]
    assert result == [0.01, 0.02, 0.03]


@pytest.mark.asyncio
async def test_collect() -> None:
    from kabukit.utils.concurrent import collect

    x = (asyncio.sleep(s, s) for s in [0.03, 0.02, 0.01])
    ait = collect(x, max_concurrency=2)
    result = [s async for s in ait]
    assert sorted(result) == [0.01, 0.02, 0.03]


@pytest.mark.asyncio
async def test_collect_fn() -> None:
    from kabukit.utils.concurrent import collect_fn

    async def sleep(s: float) -> float:
        return await asyncio.sleep(s, s)

    ait = collect_fn(sleep, [0.03, 0.02, 0.01], max_concurrency=3)
    result = [s async for s in ait]
    assert sorted(result) == [0.01, 0.02, 0.03]


async def sleep_df(second: float) -> pl.DataFrame:
    await asyncio.sleep(second)
    return pl.DataFrame({"a": [second]})


@pytest.mark.asyncio
async def test_concat() -> None:
    from kabukit.utils.concurrent import concat

    x = (sleep_df(s) for s in [0.03, 0.02, 0.01])
    df = await concat(x, max_concurrency=2)
    assert df.sort("a").to_series().to_list() == [0.01, 0.02, 0.03]


@pytest.mark.asyncio
async def test_concat_fn() -> None:
    from kabukit.utils.concurrent import concat_fn

    df = await concat_fn(sleep_df, [0.03, 0.02, 0.01], max_concurrency=2)
    assert df.sort("a").to_series().to_list() == [0.01, 0.02, 0.03]


class MockClient(Client):
    async def get_data(self, code: int) -> pl.DataFrame:
        await asyncio.sleep(0.01)
        return pl.DataFrame({"Code": [code]})


@pytest.mark.asyncio
async def test_stream() -> None:
    from kabukit.utils.concurrent import get_stream

    async with MockClient() as client:
        stream = get_stream(client, "data", args=[1, 2, 3])

        dfs = [df async for df in stream]
        assert sorted(df["Code"].to_list() for df in dfs) == [[1], [2], [3]]


@pytest.mark.asyncio
async def test_get() -> None:
    from kabukit.utils.concurrent import get

    df = await get(MockClient, "data", [1, 2, 3], max_concurrency=2)
    assert df["Code"].sort().to_list() == [1, 2, 3]


async def progress(
    ait: AsyncIterable[pl.DataFrame],
    total: int | None = None,
) -> AsyncIterator[pl.DataFrame]:
    async for x in ait:
        yield x.with_columns(pl.col("Code") * total)


@pytest.mark.asyncio
async def test_get_progress() -> None:
    from kabukit.utils.concurrent import get

    df = await get(MockClient, "data", [1, 2, 3], progress=progress)
    assert df["Code"].sort().to_list() == [3, 6, 9]


def callback(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(pl.col("Code") * 10)


@pytest.mark.asyncio
async def test_get_callback() -> None:
    from kabukit.utils.concurrent import get

    df = await get(MockClient, "data", [1, 2, 3], callback=callback)
    assert df["Code"].sort().to_list() == [10, 20, 30]


@pytest.mark.asyncio
async def test_get_with_max_items() -> None:
    from kabukit.utils.concurrent import get

    df = await get(MockClient, "data", range(10), max_items=3, max_concurrency=2)
    assert df["Code"].sort().to_list() == [0, 1, 2]
