from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from httpx import Response
from polars.testing import assert_frame_equal

from kabukit.sources.yahoo.client import YahooClient

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


async def test_get_quote(mocker: MockerFixture) -> None:
    mock_get = mocker.patch.object(YahooClient, "get")
    mock_get.return_value = Response(200, text="abc")
    mock_parse_quote = mocker.patch("kabukit.sources.yahoo.client.parse_quote")
    mock_parse_quote.return_value = pl.DataFrame({"a": 1})

    client = YahooClient()
    df = await client.get_quote("2703")

    assert_frame_equal(df, pl.DataFrame({"Code": "27030", "a": 1}))
    mock_get.assert_awaited_once_with("2703.T")
    mock_parse_quote.assert_called_once_with("abc")


async def test_get_quote_empty(mocker: MockerFixture) -> None:
    mock_get = mocker.patch.object(YahooClient, "get")
    mock_get.return_value = Response(200, text="")

    client = YahooClient()
    df = await client.get_quote("2703")

    assert_frame_equal(df, pl.DataFrame())
    mock_get.assert_awaited_once_with("2703.T")


async def test_get_performance(mocker: MockerFixture) -> None:
    mock_get = mocker.patch.object(YahooClient, "get")
    mock_get.return_value = Response(200, text="abc")
    mock_parse_performance = mocker.patch(
        "kabukit.sources.yahoo.client.parse_performance",
    )
    mock_parse_performance.return_value = pl.DataFrame({"a": 1})

    client = YahooClient()
    df = await client.get_performance("2703")

    assert_frame_equal(df, pl.DataFrame({"Code": "27030", "a": 1}))
    mock_get.assert_awaited_once_with("2703.T/performance")
    mock_parse_performance.assert_called_once_with("abc")
