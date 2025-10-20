from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from polars import col as c

from kabukit.domain.jquants.prices import Prices
from kabukit.sources.jquants.concurrent import get
from tests.validation.conftest import pytestmark  # noqa: F401

if TYPE_CHECKING:
    from kabukit.domain.jquants.statements import Statements


@pytest_asyncio.fixture(scope="module")
async def prices(statements: Statements) -> Prices:
    codes = ["7203"]
    data = await get("prices", codes)
    return Prices(data).with_equity(statements)


@pytest.mark.parametrize(
    ("d", "equity"),
    [
        (date(2025, 5, 7), 36856527000000),
        (date(2025, 5, 8), 36878913000000),
        (date(2025, 10, 3), 36993052000000),
    ],
)
def test_equity_7203(
    prices: Prices,
    d: date,
    equity: float,
) -> None:
    df = prices.data.filter(c.Code == "72030", c.Date == d)
    assert df.item(0, "Equity") == equity
