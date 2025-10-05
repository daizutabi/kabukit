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
    codes = ["7203"]  # トヨタのみ
    data = await fetch("prices", codes)
    return (
        Prices(data)
        .with_yields(statements)  # すべての利回り指標とReportDateを準備
        .with_period_stats()  # 期ごとの統計量を計算
    )


@pytest.mark.parametrize(
    ("d", "expected"),
    [
        (date(2025, 10, 3), 1.2345),
    ],
)
def test_book_value_yield_period_open_7203(
    prices: Prices,
    d: date,
    expected: float,
) -> None:
    df = prices.data.filter(c.Code == "72030", c.Date == d)
    result = df.item(0, "BookValueYield_PeriodOpen")
    assert result == pytest.approx(expected, rel=1e-2)  # pyright: ignore[reportUnknownMemberType]
