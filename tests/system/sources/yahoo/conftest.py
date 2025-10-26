from __future__ import annotations

import pytest_asyncio

from kabukit.sources.yahoo.client import YahooClient


@pytest_asyncio.fixture
async def client():
    async with YahooClient() as client:
        yield client
