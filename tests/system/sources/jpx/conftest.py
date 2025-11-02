from __future__ import annotations

import pytest_asyncio

from kabukit.sources.jpx.client import JpxClient


@pytest_asyncio.fixture
async def client():
    async with JpxClient() as client:
        yield client
