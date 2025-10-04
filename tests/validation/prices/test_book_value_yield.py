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
    return (
        Prices(data)
        .with_adjusted_shares(statements)
        .with_equity(statements)
        .with_book_value_yield()
    )


@pytest.mark.parametrize(
    ("d", "bps"),
    [
        (date(2025, 5, 7), 2814.35),
        (date(2025, 5, 8), 2826.20),
        (date(2025, 10, 3), 2838.33),
    ],
)
def test_book_value_per_share_7203(
    prices: Prices,
    d: date,
    bps: float,
) -> None:
    df = prices.data.filter(c.Code == "72030", c.Date == d)
    result = df.item(0, "BookValuePerShare")
    assert result == pytest.approx(bps, rel=1e-2)  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.parametrize(
    ("d", "bps"),
    [
        (date(2025, 9, 26), 429.90),
        (date(2025, 9, 29), 42.99),
    ],
)
def test_book_value_per_share_3997(
    prices: Prices,
    d: date,
    bps: float,
) -> None:
    df = prices.data.filter(c.Code == "39970", c.Date == d)
    result = df.item(0, "BookValuePerShare")
    assert result == pytest.approx(bps, rel=1e-2)  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.parametrize(
    ("d", "by"),
    [
        (date(2025, 5, 7), 1.0400),
        (date(2025, 5, 8), 1.0579),
        (date(2025, 10, 3), 0.9996),
    ],
)
def test_book_value_yield_7203(
    prices: Prices,
    d: date,
    by: float,
) -> None:
    df = prices.data.filter(c.Code == "72030", c.Date == d)
    result = df.item(0, "BookValueYield")
    assert result == pytest.approx(by, rel=1e-2)  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.parametrize(
    ("d", "by"),
    [
        (date(2025, 9, 26), 0.1191),
        (date(2025, 9, 29), 0.1218),
    ],
)
def test_book_value_yield_3997(
    prices: Prices,
    d: date,
    by: float,
) -> None:
    df = prices.data.filter(c.Code == "39970", c.Date == d)
    result = df.item(0, "BookValueYield")
    assert result == pytest.approx(by, rel=1e-2)  # pyright: ignore[reportUnknownMemberType]
