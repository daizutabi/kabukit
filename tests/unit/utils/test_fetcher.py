from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, ClassVar

import polars as pl
import pytest

from kabukit.sources.client import Client
from kabukit.utils.fetcher import collect, get

if TYPE_CHECKING:
    from collections.abc import AsyncIterable, AsyncIterator

pytestmark = pytest.mark.unit


async def sleep(seconds: list[float]):
    x = (asyncio.sleep(s, s) for s in seconds)
    y = asyncio.as_completed(x)
    for i in y:  # async for (python 3.13+)
        yield await i


async def test_sleep() -> None:
    ait = sleep([0.03, 0.02, 0.01])
    result = [s async for s in ait]
    assert result == [0.01, 0.02, 0.03]


async def test_collect() -> None:
    async def sleep(s: float) -> float:
        return await asyncio.sleep(s, s)

    ait = collect(sleep, [0.03, 0.02, 0.01], max_concurrency=3)
    result = [s async for s in ait]
    assert sorted(result) == [0.01, 0.02, 0.03]


async def sleep_df(second: float) -> pl.DataFrame:
    await asyncio.sleep(second)
    return pl.DataFrame({"a": [second]})


class MockClient(Client):
    base_url: ClassVar[str] = "http://mock.api"

    async def get_data(self, code: int) -> pl.DataFrame:
        await asyncio.sleep(0.01)
        return pl.DataFrame({"Code": [code]})


async def test_get() -> None:
    df = await get(MockClient, MockClient.get_data, [1, 2, 3], max_concurrency=2)
    assert df["Code"].sort().to_list() == [1, 2, 3]


async def progress(
    ait: AsyncIterable[pl.DataFrame],
    total: int | None = None,
) -> AsyncIterator[pl.DataFrame]:
    async for x in ait:
        yield x.with_columns(pl.col("Code") * total)


async def test_get_progress() -> None:
    df = await get(MockClient, MockClient.get_data, [1, 2, 3], progress=progress)
    assert df["Code"].sort().to_list() == [3, 6, 9]


def callback(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(pl.col("Code") * 10)


async def test_get_with_max_items() -> None:
    df = await get(
        MockClient,
        MockClient.get_data,
        range(10),
        max_items=3,
        max_concurrency=2,
    )
    assert df["Code"].sort().to_list() == [0, 1, 2]
