from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from httpx import Response
from polars.testing import assert_frame_equal

from kabukit.sources.edinet.client import EdinetClient

if TYPE_CHECKING:
    from typing import Any
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_list_success(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    results = [{"docID": "S100TEST"}]
    json = {"results": results}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    expected_df = pl.DataFrame(results)
    mock_clean_list = mocker.patch("kabukit.sources.edinet.client.clean_list")
    mock_clean_list.return_value = expected_df

    mock_with_date = mocker.patch("kabukit.sources.edinet.client.with_date")
    mock_with_date.return_value = expected_df

    client = EdinetClient("test_key")
    date = "2023-10-26"
    df = await client.get_list(date)

    assert_frame_equal(df, expected_df)
    mock_get.assert_awaited_once_with(
        "/documents.json",
        params={"date": date, "type": 2},
    )
    mock_clean_list.assert_called_once()
    mock_with_date.assert_called_once()


@pytest.mark.asyncio
async def test_get_list_no_results(
    mock_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    json = {"metadata": {"status": "200"}}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    df = await client.get_list("2023-10-26")

    assert df.is_empty()


@pytest.mark.asyncio
async def test_get_list_empty_results(
    mock_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    json: dict[str, list[Any]] = {"results": []}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    df = await client.get_list("2023-10-26")

    assert df.is_empty()
