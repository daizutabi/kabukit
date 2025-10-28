from __future__ import annotations

import datetime
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


async def test_get_topix(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"topix": [{"Date": "2025-01-01", "Open": 100}]}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    result = await client.get_topix()

    expected = pl.DataFrame(
        {
            "Date": [datetime.date(2025, 1, 1)],
            "Code": ["TOPIX"],
            "Open": [100],
        },
    )

    assert_frame_equal(result, expected)


async def test_empty(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json: dict[str, list[dict[str, str]]] = {"topix": []}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_topix()
    assert df.is_empty()
