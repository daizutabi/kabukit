from __future__ import annotations

import random

import pytest

from kabukit.sources.yahoo.fetcher import get_quote

pytestmark = pytest.mark.system


async def test_get_quote_code(codes: list[str]) -> None:
    df = await get_quote(codes[0])
    assert df.shape == (1, 24)


async def test_get_quote_codes(codes: list[str]) -> None:
    codes = codes[:]
    random.shuffle(codes)
    df = await get_quote(codes)
    assert df.shape == (len(codes), 24)
    assert df["Code"].to_list() == sorted(f"{c}0" for c in codes)


async def test_get_quote_without_code() -> None:
    df = await get_quote(max_items=3)
    assert df.shape == (3, 24)
