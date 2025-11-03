from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pytest
import pytest_asyncio

from kabukit.sources.tdnet.client import TdnetClient

if TYPE_CHECKING:
    import datetime


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
    async with TdnetClient() as client:
        for date in dates:
            page = await client.get_page(date, 1)
            if 'id="pager-box-top"' in page:
                return date

    raise NotImplementedError


@pytest_asyncio.fixture(scope="module")
async def page(date: datetime.date):
    async with TdnetClient() as client:
        yield await client.get_page(date, 1)


@pytest_asyncio.fixture(scope="module")
async def data(date: datetime.date):
    async with TdnetClient() as client:
        yield await client.get_list(date)


@pytest_asyncio.fixture(scope="module")
async def xbrl_urls(dates: list[datetime.date]) -> list[str]:
    urls: list[str] = []

    async with TdnetClient() as client:
        for date in dates:
            async for item in client.iter_items(date):
                if item.xbrl_url is not None:
                    urls.append(item.xbrl_url)
                if len(urls) >= 20:
                    return random.sample(urls, 10)

    raise NotImplementedError


@pytest.fixture(scope="module", params=range(10))
def xbrl_url(xbrl_urls: list[str], request: pytest.FixtureRequest) -> str:
    assert isinstance(request.param, int)
    return xbrl_urls[request.param]


@pytest_asyncio.fixture(scope="module")
async def xbrl_content(xbrl_url: str) -> bytes:
    async with TdnetClient() as client:
        response = await client.get(xbrl_url)
        return response.content
