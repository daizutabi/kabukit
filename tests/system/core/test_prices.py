from __future__ import annotations

import polars as pl
import pytest
import pytest_asyncio

from kabukit.core.prices import Prices
from kabukit.sources.jquants.client import JQuantsClient

pytestmark = pytest.mark.system


@pytest_asyncio.fixture(scope="module")
async def prices():
    async with JQuantsClient() as client:
        data = await client.get_prices("6200")
        yield Prices(data)


def test_prices_data(prices: Prices) -> None:
    assert not prices.data.is_empty()
    assert "Date" in prices.data.columns
    assert "Code" in prices.data.columns
    assert prices.data["Code"].unique().to_list() == ["62000"]


def test_adjustment_factor(prices: Prices) -> None:
    df = prices.data.filter(pl.col("AdjustmentFactor") != 1)
    assert df.height == 4
