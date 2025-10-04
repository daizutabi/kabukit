from datetime import date

import pytest
import pytest_asyncio
from polars import col as c

from kabukit.core.prices import Prices
from kabukit.core.statements import Statements
from kabukit.jquants.concurrent import fetch
from tests.validation.conftest import pytestmark  # noqa: F401


@pytest_asyncio.fixture(scope="module")
async def prices(statements: Statements) -> Prices:
    codes = ["7203", "3997"]
    data = await fetch("prices", codes)
    return Prices(data).with_adjusted_shares(statements).with_market_cap()


@pytest.mark.parametrize(
    ("d", "market_cap"),
    [
        (date(2025, 5, 7), 35437527543198),
        (date(2025, 5, 8), 34860215891241),
        (date(2025, 10, 3), 37008314437338),
    ],
)
def test_market_cap_7203(
    prices: Prices,
    d: date,
    market_cap: float,
) -> None:
    df = prices.data.filter(c.Code == "72030", c.Date == d)
    assert df.item(0, "MarketCap") == market_cap


@pytest.mark.parametrize(
    ("d", "market_cap"),
    [
        (date(2025, 9, 26), 14082176800),
        (date(2025, 9, 29), 13770106400),
        (date(2025, 10, 3), 10766428800),
    ],
)
def test_market_cap_3997(
    prices: Prices,
    d: date,
    market_cap: float,
) -> None:
    df = prices.data.filter(c.Code == "39970", c.Date == d)
    assert df.item(0, "MarketCap") == market_cap
