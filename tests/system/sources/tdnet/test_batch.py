from __future__ import annotations

import datetime

import pytest
import pytest_asyncio

pytestmark = pytest.mark.system


@pytest_asyncio.fixture(scope="module")
async def dates():
    from kabukit.sources.jquants.client import JQuantsClient
    from kabukit.utils.datetime import today

    date = today()

    async with JQuantsClient() as client:
        df = await client.get_calendar(
            holidaydivision="1",
            from_=date - datetime.timedelta(7),
            to=date,
        )

    return df["Date"].to_list()


async def test_get_list_single_date(dates: list[datetime.date]) -> None:
    from kabukit.sources.tdnet.batch import get_list

    date = dates[0]
    df = await get_list(date)
    dates = df["DisclosedDate"].unique().to_list()

    if dates:
        assert len(dates) == 1
        assert dates[0] == date


async def test_get_list_multiple_dates(dates: list[datetime.date]) -> None:
    from kabukit.sources.tdnet.batch import get_list

    df = await get_list(dates)
    result = df["DisclosedDate"].unique().to_list()
    assert result
    assert all(date in dates for date in result)


async def test_get_list_without_dates() -> None:
    from kabukit.sources.tdnet.batch import get_list

    df = await get_list()
    dates = df["DisclosedDate"].unique().to_list()
    assert len(dates) >= 18


async def test_get_list_invalid_date() -> None:
    from kabukit.sources.tdnet.batch import get_list

    df = await get_list("1000-01-01")
    assert df.is_empty()


async def test_get_list_future_date() -> None:
    from kabukit.sources.tdnet.batch import get_list
    from kabukit.utils.datetime import today

    date = today() + datetime.timedelta(1)
    df = await get_list(date)
    assert df.is_empty()
