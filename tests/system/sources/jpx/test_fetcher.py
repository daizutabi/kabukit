from __future__ import annotations

import pytest

from kabukit.sources.jpx.fetcher import get_shares

pytestmark = pytest.mark.system


async def test_get_shares() -> None:
    df = await get_shares(max_items=2)
    company = df["Company"].to_list()
    assert company[0] == "極洋"
    assert company[1] == "極洋"
    assert company[2] != "極洋"
