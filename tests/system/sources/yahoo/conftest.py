from __future__ import annotations

import pytest
import pytest_asyncio

from kabukit.sources.yahoo.client import YahooClient


@pytest.fixture(scope="module", params=["7203"])
def code(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest_asyncio.fixture(scope="module")
async def state(code: str):
    async with YahooClient() as client:
        response = await client.get(f"{code}.T")
        yield response.text


@pytest.fixture(scope="module")
async def quote(state: str):
    from kabukit.sources.yahoo.parser import get_preloaded_state

    return get_preloaded_state(state)
