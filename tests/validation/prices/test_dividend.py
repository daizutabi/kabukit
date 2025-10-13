from datetime import date

import pytest
import pytest_asyncio
from polars import col as c

from kabukit.core.prices import Prices
from kabukit.core.statements import Statements
from kabukit.jquants.concurrent import get
from tests.validation.conftest import pytestmark  # noqa: F401


@pytest_asyncio.fixture(scope="module")
async def prices(statements: Statements) -> Prices:
    codes = ["7203", "3997"]
    data = await get("prices", codes)
    return Prices(data).with_forecast_dividend(statements)


@pytest.mark.parametrize(
    ("d", "dividend"),
    [
        (date(2025, 5, 7), 1193416845132),
        (date(2025, 5, 8), 1239634634003),
        (date(2025, 10, 3), 1238179234651),
    ],
)
def test_forecast_dividend_7203(
    prices: Prices,
    d: date,
    dividend: float,
) -> None:
    df = prices.data.filter(c.Code == "72030", c.Date == d)
    assert df.item(0, "ForecastDividend") == dividend


@pytest.mark.parametrize(
    ("d", "dividend"),
    [
        (date(2024, 12, 27), 69120539),
        (date(2025, 5, 12), 68917988),
        (date(2025, 10, 3), 68965517),
    ],
)
def test_forecast_dividend_3997(
    prices: Prices,
    d: date,
    dividend: float,
) -> None:
    df = prices.data.filter(c.Code == "39970", c.Date == d)
    assert df.item(0, "ForecastDividend") == dividend
