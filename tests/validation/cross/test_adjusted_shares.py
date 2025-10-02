import pytest_asyncio
from polars import col as c

from kabukit.core.prices import Prices
from kabukit.core.statements import Statements
from kabukit.jquants.concurrent import fetch
from tests.validation.conftest import pytestmark  # noqa: F401


@pytest_asyncio.fixture(scope="module")
async def prices() -> Prices:
    codes = ["3350", "6200", "3399", "7187", "6542", "3816", "4923", "3997"]
    data = await fetch("prices", codes)
    return Prices(data)


def test_adjusted_shares(prices: Prices, statements: Statements) -> None:
    data = prices.with_adjusted_shares(statements).data

    df = (
        data.with_columns(
            MarketCap=c.RawClose * c.AdjustedTotalShares,
        )
        .with_columns(PrevMarketCap=c.MarketCap.shift(1).over("Code"))
        .filter(c.AdjustmentFactor != 1)
        .with_columns(Ratio=(c.MarketCap - c.PrevMarketCap).abs() / c.PrevMarketCap)
    )

    x = df["Ratio"].mean()
    assert isinstance(x, float)
    assert x < 0.05

    x = df["Ratio"].max()
    assert isinstance(x, float)
    assert x < 0.25
