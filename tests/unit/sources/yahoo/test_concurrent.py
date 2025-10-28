from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from kabukit.sources.yahoo import concurrent
from kabukit.sources.yahoo.client import YahooClient

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


async def test_get_quote_single_code(mocker: MockerFixture) -> None:
    mock_df = pl.DataFrame({"Code": [1]})
    mock_get_quote_method = mocker.AsyncMock(return_value=mock_df)
    mocker.patch.object(YahooClient, "get_quote", new=mock_get_quote_method)

    result = await concurrent.get_quote("2703")

    mock_get_quote_method.assert_awaited_once_with("2703")
    assert_frame_equal(result, mock_df)


async def test_get_quote_multiple_codes(mocker: MockerFixture) -> None:
    mock_df = pl.DataFrame({"Code": [3, 2, 1]})
    mock_concurrent_get = mocker.AsyncMock(return_value=mock_df)
    mocker.patch(
        "kabukit.sources.yahoo.concurrent.concurrent.get",
        new=mock_concurrent_get,
    )

    codes = ["1", "2", "3"]
    result = await concurrent.get_quote(codes)

    mock_concurrent_get.assert_awaited_once_with(
        YahooClient,
        "quote",
        codes,
        max_items=None,
        max_concurrency=12,
        progress=None,
        callback=None,
    )
    assert_frame_equal(result, mock_df.sort("Code"))


async def test_get_quote_no_codes_specified(mocker: MockerFixture) -> None:
    codes = ["1", "2", "3"]
    mock_get_target_codes = mocker.AsyncMock(return_value=codes)
    mocker.patch(
        "kabukit.sources.yahoo.concurrent.get_target_codes",
        new=mock_get_target_codes,
    )

    mock_df = pl.DataFrame({"Code": [3, 2, 1]})
    mock_concurrent_get = mocker.AsyncMock(return_value=mock_df)
    mocker.patch(
        "kabukit.sources.yahoo.concurrent.concurrent.get",
        new=mock_concurrent_get,
    )

    result = await concurrent.get_quote()

    mock_get_target_codes.assert_awaited_once()
    mock_concurrent_get.assert_awaited_once_with(
        YahooClient,
        "quote",
        codes,
        max_items=None,
        max_concurrency=12,
        progress=None,
        callback=None,
    )
    assert_frame_equal(result, mock_df.sort("Code"))
