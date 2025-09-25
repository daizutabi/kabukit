import asyncio

import pytest
from polars import DataFrame


async def sleep(seconds: list[float]):
    x = (asyncio.sleep(s, s) for s in seconds)
    y = asyncio.as_completed(x)
    async for i in y:
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


async def sleep_df(second: float) -> DataFrame:
    await asyncio.sleep(second)
    return DataFrame({"a": [second]})


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
