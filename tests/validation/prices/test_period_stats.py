from datetime import date

import pytest
import pytest_asyncio
from polars import DataFrame
from polars import col as c

from kabukit.core.prices import Prices
from kabukit.core.statements import Statements
from kabukit.jquants.concurrent import fetch
from tests.validation.conftest import pytestmark  # noqa: F401


@pytest_asyncio.fixture(scope="module")
async def data(statements: Statements) -> DataFrame:
    codes = ["7203"]  # トヨタのみ
    data = await fetch("prices", codes)
    return Prices(data).with_yields(statements).period_stats()


@pytest.mark.parametrize(
    ("d", "expected"),
    [
        (date(2025, 8, 7), 1.059077),
    ],
)
def test_book_value_yield_period_open_7203(
    data: DataFrame,
    d: date,
    expected: float,
) -> None:
    df = data.filter(c.Code == "72030", c.ReportDate == d)
    result = df.item(0, "BookValueYield_PeriodOpen")
    assert result == pytest.approx(expected, rel=1e-2)  # pyright: ignore[reportUnknownMemberType]
