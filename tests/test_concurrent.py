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
