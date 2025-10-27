from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_async_with() -> None:
    from kabukit.sources.client import Client

    async with Client() as client:
        assert not client.client.is_closed

    assert client.client.is_closed
