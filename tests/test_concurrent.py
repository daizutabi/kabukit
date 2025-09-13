import pytest

from kabukit.jquants.client import JQuantsClient


@pytest.mark.asyncio
async def test_fetch():
    from kabukit.concurrent import fetch

    client = JQuantsClient()
    df = await fetch(client.get_prices, ["1301", "1332"])
    assert df["Code"].n_unique() == 2
    assert "13010" in df["Code"]
    assert "13320" in df["Code"]


async def sleep(seconds: list[float]):
    import asyncio

    x = (asyncio.sleep(s, s) for s in seconds)
    y = asyncio.as_completed(x)
    async for i in y:
        yield await i


@pytest.mark.asyncio
async def test_sleep():
    ait = sleep([0.3, 0.2, 0.1])
    result = [s async for s in ait]
    assert result == [0.1, 0.2, 0.3]
