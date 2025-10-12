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
    return (
        Prices(data)
        .with_adjusted_shares(statements)
        .with_forecast_profit(statements)
        .with_earnings_yield()
    )


@pytest.mark.parametrize(
    ("d", "eps"),
    [
        (date(2025, 5, 7), 345.15),
        (date(2025, 5, 8), 237.57),
        (date(2025, 10, 3), 204.09),
    ],
)
def test_earnings_per_share_7203(
    prices: Prices,
    d: date,
    eps: float,
) -> None:
    df = prices.data.filter(c.Code == "72030", c.Date == d)
    result = df.item(0, "EarningsPerShare")
    assert result == pytest.approx(eps, rel=1e-2)  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.parametrize(
    ("d", "eps"),
    [
        (date(2025, 9, 26), 25.64),
        (date(2025, 9, 29), 2.56),
    ],
)
def test_earnings_per_share_3997(
    prices: Prices,
    d: date,
    eps: float,
) -> None:
    df = prices.data.filter(c.Code == "39970", c.Date == d)
    result = df.item(0, "EarningsPerShare")
    assert result == pytest.approx(eps, rel=1e-2)  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.parametrize(
    ("d", "ey"),
    [
        (date(2025, 5, 7), 0.1275),
        (date(2025, 5, 8), 0.0889),
        (date(2025, 10, 3), 0.0719),
    ],
)
def test_earnings_yield_7203(
    prices: Prices,
    d: date,
    ey: float,
) -> None:
    df = prices.data.filter(c.Code == "72030", c.Date == d)
    result = df.item(0, "EarningsYield")
    assert result == pytest.approx(ey, rel=1e-2)  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.parametrize(
    ("d", "ey"),
    [
        (date(2025, 9, 26), 0.0071),
        (date(2025, 9, 29), 0.0073),
    ],
)
def test_earnings_yield_3997(
    prices: Prices,
    d: date,
    ey: float,
) -> None:
    df = prices.data.filter(c.Code == "39970", c.Date == d)
    result = df.item(0, "EarningsYield")
    assert result == pytest.approx(ey, rel=1e-2)  # pyright: ignore[reportUnknownMemberType]
