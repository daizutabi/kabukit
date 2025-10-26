from __future__ import annotations

from typing import TYPE_CHECKING

import pytest_asyncio

from kabukit.sources.yahoo.client import YahooClient

if TYPE_CHECKING:
    import datetime
    from typing import Any


@pytest_asyncio.fixture
async def client():
    async with YahooClient() as client:
        yield client


@pytest_asyncio.fixture(scope="module")
async def state():
    async with YahooClient() as client:
        yield await client.get_state("72030")


@pytest_asyncio.fixture(scope="module")
async def main_stocks_detail(state: dict[str, Any]) -> datetime.date:
    return state["mainStocksDetail"]
