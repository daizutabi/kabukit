from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from kabukit.sources.yahoo.client import PRELOADED_STATE_PATTERN

if TYPE_CHECKING:
    from kabukit.sources.yahoo.client import YahooClient

pytestmark = pytest.mark.system


@pytest.mark.asyncio
async def test_response_has_preloaded_state(client: YahooClient) -> None:
    resp = await client.get("7203.T")
    assert PRELOADED_STATE_PATTERN.search(resp.text) is not None


@pytest.mark.asyncio
async def test_get_state(client: YahooClient) -> None:
    state = await client.get_state("72030")
    assert isinstance(state, dict)
