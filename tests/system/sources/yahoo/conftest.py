from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
import pytest_asyncio

from kabukit.sources.yahoo.client import YahooClient
from kabukit.sources.yahoo.parser import get_preloaded_state, get_preloaded_store

if TYPE_CHECKING:
    from collections.abc import Callable


async def get(url: str, parser: Callable[[str], dict[str, Any]]) -> dict[str, Any]:
    async with YahooClient() as client:
        response = await client.get(url)
        return parser(response.text)


@pytest.fixture(scope="module", params=["7203"])
def code(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest_asyncio.fixture(scope="module")
async def quote(code: str):
    return await get(f"{code}.T", get_preloaded_state)


@pytest_asyncio.fixture(scope="module")
async def performance(code: str):
    return await get(f"{code}.T/performance", get_preloaded_store)
