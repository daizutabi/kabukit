from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from httpx import Response
from polars.testing import assert_frame_equal

from kabukit.sources.jquants.client import JQuantsClient

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


async def test_get_info(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"info": [{"Date": "2023-01-01", "Code": "7203"}]}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_info(transform=False, only_common_stocks=False)
    assert df["Date"].to_list() == ["2023-01-01"]
    assert df["Code"].to_list() == ["7203"]


async def test_get_info_empty(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    response = Response(200, json={"info": []})
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_info()
    assert_frame_equal(df, pl.DataFrame())


async def test_get_info_transform(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"info": [{"Code": "7203"}, {"Code": "9999"}]}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    mock_transform = mocker.patch(
        "kabukit.sources.jquants.client.info.transform",
        return_value=pl.DataFrame({"Code": ["7203"]}),
    )

    client = JQuantsClient("test_token")
    df = await client.get_info(transform=True, only_common_stocks=True)
    assert df["Code"].to_list() == ["7203"]
    mock_transform.assert_called_once_with(mocker.ANY, only_common_stocks=True)
