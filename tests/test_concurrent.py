import asyncio

import pytest


async def sleep(seconds: list[float]):
    x = (asyncio.sleep(s, s) for s in seconds)
    y = asyncio.as_completed(x)
    async for i in y:
        yield await i


@pytest.mark.asyncio
async def test_sleep():
    ait = sleep([0.03, 0.02, 0.01])
    result = [s async for s in ait]
    assert result == [0.01, 0.02, 0.03]


@pytest.mark.asyncio
async def test_collect():
    from src.kabukit.concurrent import collect

    x = (asyncio.sleep(s, s) for s in [0.03, 0.02, 0.01])
    ait = collect(x, max_concurrency=2)
    result = [s async for s in ait]
    assert sorted(result) == [0.01, 0.02, 0.03]


@pytest.mark.asyncio
async def test_collect_fn():
    from src.kabukit.concurrent import collect_fn

    async def sleep(s: float) -> float:
        return await asyncio.sleep(s, s)

    ait = collect_fn(sleep, [0.03, 0.02, 0.01], max_concurrency=3)
    result = [s async for s in ait]
    assert sorted(result) == [0.01, 0.02, 0.03]
