from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from polars import col as c

from kabukit.domain.jquants.prices import Prices
from kabukit.sources.jquants.concurrent import get_prices
from tests.validation.conftest import pytestmark  # noqa: F401

if TYPE_CHECKING:
    from kabukit.domain.jquants.statements import Statements


@pytest_asyncio.fixture(scope="module")
async def prices(statements: Statements) -> Prices:
    codes = ["7203", "3997"]
    data = await get_prices(codes)
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
