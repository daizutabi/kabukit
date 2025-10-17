from datetime import date

import pytest
import pytest_asyncio
from polars import col as c

from kabukit.core.prices import Prices
from kabukit.core.statements import Statements
from kabukit.sources.jquants.concurrent import get
from tests.validation.conftest import pytestmark  # noqa: F401


@pytest_asyncio.fixture(scope="module")
async def prices(statements: Statements) -> Prices:
    codes = ["7203", "3997"]
    data = await get("prices", codes)
    return Prices(data).with_forecast_profit(statements)


@pytest.mark.parametrize(
    ("d", "profit"),
    [
        (date(2025, 5, 7), 4520000000000),
        (date(2025, 5, 8), 3100000000000),
        (date(2025, 10, 3), 2660000000000),
    ],
)
def test_forecast_profit_7203(
    prices: Prices,
    d: date,
    profit: float,
) -> None:
    df = prices.data.filter(c.Code == "72030", c.Date == d)
    assert df.item(0, "ForecastProfit") == profit


@pytest.mark.parametrize(
    ("d", "profit"),
    [
        (date(2025, 1, 10), -123000000),
        (date(2025, 10, 3), 100000000),
    ],
)
def test_forecast_profit_3997(
    prices: Prices,
    d: date,
    profit: float,
) -> None:
    df = prices.data.filter(c.Code == "39970", c.Date == d)
    assert df.item(0, "ForecastProfit") == profit
