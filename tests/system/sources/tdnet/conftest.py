from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio

from kabukit.sources.tdnet.client import TdnetClient

if TYPE_CHECKING:
    import datetime

    from bs4.element import Tag


@pytest_asyncio.fixture
async def client():
    async with TdnetClient() as client:
        yield client


@pytest_asyncio.fixture(scope="module")
async def dates():
    async with TdnetClient() as client:
        yield await client.get_dates()


@pytest_asyncio.fixture(scope="module")
async def date(dates: list[datetime.date]) -> datetime.date:
    for date in dates:
        if date.weekday() == 0:
            return date

    raise NotImplementedError


@pytest_asyncio.fixture(scope="module")
async def page(date: datetime.date):
    async with TdnetClient() as client:
        yield await client.get_page(date, 1)


@pytest.fixture(scope="module")
def table(page: str) -> Tag:
    from kabukit.sources.tdnet.document import get_table

    table = get_table(page)
    assert table is not None
    return table


@pytest_asyncio.fixture(scope="module")
async def data(date: datetime.date):
    async with TdnetClient() as client:
        yield await client.get_list(date)
