from __future__ import annotations

from typing import Any

import pytest
import pytest_asyncio

from kabukit.sources.yahoo.client import YahooClient
from kabukit.sources.yahoo.parser import get_preloaded_state, get_preloaded_store


async def get(url: str) -> str:
    async with YahooClient() as client:
        response = await client.get(url)
        return response.text


@pytest.fixture(scope="module", params=["7203"])
def code(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest_asyncio.fixture(scope="module")
async def quote(code: str) -> str:
    return await get(f"{code}.T")


@pytest_asyncio.fixture(scope="module")
async def performance(code: str) -> str:
    return await get(f"{code}.T/performance")


@pytest.fixture(scope="module")
def state(quote: str) -> dict[str, Any]:
    return get_preloaded_state(quote)


@pytest.fixture(scope="module")
def store(performance: str) -> dict[str, Any]:
    return get_preloaded_store(performance)
