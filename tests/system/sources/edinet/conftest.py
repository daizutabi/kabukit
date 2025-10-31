from __future__ import annotations

import pytest_asyncio

from kabukit.sources.edinet.client import EdinetClient


@pytest_asyncio.fixture
async def client():
    async with EdinetClient() as client:
        yield client
