from __future__ import annotations

from typing import Any

import pytest
import pytest_asyncio

from kabukit.sources.yahoo.client import YahooClient
from kabukit.sources.yahoo.parser import get_preloaded_state, get_preloaded_store


@pytest_asyncio.fixture
async def client():
    async with YahooClient() as client:
        yield client


async def get(url: str) -> str:
    async with YahooClient() as client:
        response = await client.get(url)
        return response.text


@pytest.fixture(scope="module")
def codes() -> list[str]:
    return ["1375", "6857", "7203", "1773", "6208"]


@pytest.fixture(scope="module", params=range(5))
def code(codes: list[str], request: pytest.FixtureRequest) -> str:
    assert isinstance(request.param, int)
    return codes[request.param]


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
