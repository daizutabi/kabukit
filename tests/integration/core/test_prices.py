import polars as pl
import pytest
import pytest_asyncio
from polars import DataFrame

from kabukit.core.prices import Prices
from kabukit.jquants.client import JQuantsClient


@pytest_asyncio.fixture(scope="module")
async def prices():
    async with JQuantsClient() as client:
        data = await client.get_prices("6200")
        yield Prices(data)


@pytest.mark.integration
def test_prices_data(prices: Prices) -> None:
    assert not prices.data.is_empty()
    assert "Date" in prices.data.columns
    assert "Code" in prices.data.columns
    assert prices.data["Code"].unique().to_list() == ["62000"]


@pytest.mark.integration
def test_adjustment_factor(prices: Prices) -> None:
    df = prices.data.filter(pl.col("AdjustmentFactor") != 1)
    assert df.height == 4


@pytest_asyncio.fixture(scope="module")
async def stmts():
    async with JQuantsClient() as client:
        yield await client.get_statements("6200")


@pytest.mark.integration
def test_statements(stmts: DataFrame) -> None:
    assert not stmts.is_empty()
    assert "Date" in stmts.columns
    assert "Code" in stmts.columns
    assert stmts["Code"].unique().to_list() == ["62000"]
