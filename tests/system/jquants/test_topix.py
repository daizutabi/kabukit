from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from kabukit.sources.jquants.client import JQuantsClient

pytestmark = pytest.mark.system


@pytest.mark.asyncio
async def test_get(client: JQuantsClient) -> None:
    df = await client.get_topix(from_="2025-01-01", to="2025-01-31")
    assert df.shape == (19, 6)
    assert df.item(0, "Date") == datetime.date(2025, 1, 6)
    assert df.item(18, "Date") == datetime.date(2025, 1, 31)
    assert df["Code"].eq("TOPIX").all()


@pytest.mark.asyncio
async def test_empty(client: JQuantsClient) -> None:
    df = await client.get_topix(from_="2025-01-01", to="2025-01-01")
    assert df.is_empty()
