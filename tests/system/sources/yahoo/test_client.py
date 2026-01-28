from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal

if TYPE_CHECKING:
    from kabukit.sources.yahoo.client import YahooClient

pytestmark = pytest.mark.system


async def test_get_quote(client: YahooClient, code: str) -> None:
    df = await client.get_quote(code)
    assert df.shape == (1, 24)


async def test_get_performance(client: YahooClient, code: str) -> None:
    df = await client.get_performance(code)
    assert df.shape in [(3, 36), (0, 0)]


async def test_get_invalid_code(client: YahooClient) -> None:
    df = await client.get_quote("invalid_code")
    assert_frame_equal(df, pl.DataFrame())
