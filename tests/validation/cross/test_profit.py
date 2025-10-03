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
    codes = ["7203"]
    data = await fetch("prices", codes)
    return Prices(data).with_forecast_profit(statements)


@pytest.mark.parametrize(
    ("d", "n"),
    [
        (date(2025, 5, 7), 4520000000000),
        (date(2025, 5, 8), 3100000000000),
    ],
)
def test_forecast_profit_7203(
    prices: Prices,
    d: date,
    n: float,
) -> None:
    x = prices.data.filter(c.Code == "72030", c.Date == d).item(0, "ForecastProfit")
    assert x == n
