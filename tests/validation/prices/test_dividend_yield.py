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
    return (
        Prices(data)
        .with_adjusted_shares(statements)
        .with_forecast_dividend(statements)
        .with_dividend_yield()
    )


@pytest.mark.parametrize(
    ("d", "dps"),
    [
        (date(2025, 5, 7), 91.1289),
        (date(2025, 5, 8), 94.9989),
        (date(2025, 10, 3), 95.00),
    ],
)
def test_dividend_per_share_7203(
    prices: Prices,
    d: date,
    dps: float,
) -> None:
    df = prices.data.filter(c.Code == "72030", c.Date == d)
    result = df.item(0, "DividendPerShare")
    assert result == pytest.approx(dps, rel=1e-2)  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.parametrize(
    ("d", "dps"),
    [
        (date(2025, 9, 26), 17.679476),
        (date(2025, 9, 29), 1.767947),
    ],
)
def test_dividend_per_share_3997(
    prices: Prices,
    d: date,
    dps: float,
) -> None:
    df = prices.data.filter(c.Code == "39970", c.Date == d)
    result = df.item(0, "DividendPerShare")
    assert result == pytest.approx(dps, rel=1e-2)  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.parametrize(
    ("d", "dy"),
    [
        (date(2025, 5, 7), 0.03367),
        (date(2025, 5, 8), 0.03556),
        (date(2025, 10, 3), 0.033456),
    ],
)
def test_dividend_yield_7203(
    prices: Prices,
    d: date,
    dy: float,
) -> None:
    df = prices.data.filter(c.Code == "72030", c.Date == d)
    result = df.item(0, "DividendYield")
    assert result == pytest.approx(dy, rel=1e-2)  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.parametrize(
    ("d", "dy"),
    [
        (date(2025, 9, 26), 0.0048973),
        (date(2025, 9, 29), 0.0050084),
    ],
)
def test_dividend_yield_3997(
    prices: Prices,
    d: date,
    dy: float,
) -> None:
    df = prices.data.filter(c.Code == "39970", c.Date == d)
    result = df.item(0, "DividendYield")
    assert result == pytest.approx(dy, rel=1e-2)  # pyright: ignore[reportUnknownMemberType]
