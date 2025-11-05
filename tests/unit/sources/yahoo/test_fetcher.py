from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from kabukit.sources.yahoo.client import YahooClient
from kabukit.sources.yahoo.fetcher import get_quote

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


async def test_get_quote_single_code(mocker: MockerFixture) -> None:
    mock_df = pl.DataFrame({"Code": [1]})
    mock_get_quote_method = mocker.AsyncMock(return_value=mock_df)
    mocker.patch.object(YahooClient, "get_quote", new=mock_get_quote_method)

    result = await get_quote("2703")

    mock_get_quote_method.assert_awaited_once_with("2703")
    assert_frame_equal(result, mock_df)


async def test_get_quote_multiple_codes(
    mocker: MockerFixture,
    mock_fetcher_get: AsyncMock,
) -> None:
    mock_df = pl.DataFrame({"Code": [3, 2, 1]})
    mock_fetcher_get.return_value = mock_df

    codes = ["1", "2", "3"]
    result = await get_quote(codes)

    mock_fetcher_get.assert_awaited_once_with(
        YahooClient,
        YahooClient.get_quote,
        codes,
        max_items=None,
        max_concurrency=mocker.ANY,
        progress=None,
    )
    assert_frame_equal(result, mock_df.sort("Code"))


async def test_get_quote_no_codes_specified(
    mocker: MockerFixture,
    mock_fetcher_get: AsyncMock,
) -> None:
    codes = ["1", "2", "3"]

    mock_get_target_codes = mocker.patch(
        "kabukit.sources.yahoo.fetcher.get_target_codes",
        return_value=codes,
    )

    mock_df = pl.DataFrame({"Code": [3, 2, 1]})
    mock_fetcher_get.return_value = mock_df

    result = await get_quote()

    mock_get_target_codes.assert_awaited_once_with()
    mock_fetcher_get.assert_awaited_once_with(
        YahooClient,
        YahooClient.get_quote,
        codes,
        max_items=None,
        max_concurrency=mocker.ANY,
        progress=None,
    )
    assert_frame_equal(result, mock_df.sort("Code"))
