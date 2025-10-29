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
    text = """\
        <script>
            window.__PRELOADED_STATE__ = {"key": "value"};
        </script>
    """
    mock_get = mocker.patch.object(YahooClient, "get")
    mock_get.return_value = Response(200, text=text)

    client = YahooClient()
    df = await client.get_quote("2703")

    assert df["Code"].unique().to_list() == ["27030"]
    mock_get.assert_awaited_once_with("2703.T")


async def test_get_quote_empty(mocker: MockerFixture) -> None:
    mock_get = mocker.patch.object(YahooClient, "get")
    mock_get.return_value = Response(200, text="")

    client = YahooClient()
    df = await client.get_quote("2703")

    assert_frame_equal(df, pl.DataFrame())
    mock_get.assert_awaited_once_with("2703.T")
