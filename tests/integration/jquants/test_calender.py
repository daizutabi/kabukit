from datetime import date

import polars as pl
import pytest
import pytest_asyncio
from polars import DataFrame

from kabukit.jquants.client import JQuantsClient

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture(scope="module")
async def df():
    async with JQuantsClient() as client:
        yield await client.get_calendar()


@pytest.mark.parametrize(
    ("d", "is_holiday"),
    [
        (date(2025, 10, 4), True),
        (date(2025, 10, 5), True),
        (date(2025, 10, 6), False),
        (date(2025, 10, 10), False),
        (date(2025, 10, 11), True),
        (date(2025, 10, 12), True),
        (date(2025, 10, 13), True),
        (date(2025, 10, 14), False),
    ],
)
def test_is_holiday(df: DataFrame, d: date, *, is_holiday: bool) -> None:
    assert df.filter(pl.col("Date") == d).item(0, "IsHoliday") == is_holiday
