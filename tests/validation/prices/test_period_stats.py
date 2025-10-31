from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import polars as pl
import pytest
import pytest_asyncio
from polars import col as c

from kabukit.domain.jquants.prices import Prices
from kabukit.sources.jquants.batch import get_prices
from tests.validation.conftest import pytestmark  # noqa: F401

if TYPE_CHECKING:
    from kabukit.domain.jquants.statements import Statements


@pytest_asyncio.fixture(scope="module")
async def data(statements: Statements) -> pl.DataFrame:
    codes = ["7203"]  # トヨタのみ
    data = await get_prices(codes)
    return Prices(data).with_yields(statements).period_stats()


@pytest.mark.parametrize(
    ("d", "expected"),
    [
        (date(2025, 8, 7), 1.059077),
    ],
)
def test_book_value_yield_period_open_7203(
    data: pl.DataFrame,
    d: date,
    expected: float,
) -> None:
    df = data.filter(c.Code == "72030", c.ReportDate == d)
    result = df.item(0, "BookValueYield_PeriodOpen")
    assert result == pytest.approx(expected, rel=1e-2)  # pyright: ignore[reportUnknownMemberType]
