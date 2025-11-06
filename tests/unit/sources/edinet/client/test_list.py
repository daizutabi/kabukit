from __future__ import annotations

from typing import TYPE_CHECKING, Any

import polars as pl
import pytest
from httpx import Response
from polars.testing import assert_frame_equal

from kabukit.sources.edinet.client import EdinetClient

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


async def test_get_list_success(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    results = [{"docID": "S100TEST"}]
    json = {"results": results}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    expected_df = pl.DataFrame(results)
    mock_transform_list = mocker.patch("kabukit.sources.edinet.client.transform_list")
    mock_transform_list.return_value = expected_df

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
    mock_transform_list.assert_called_once()
    mock_with_date.assert_called_once()


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


@pytest.mark.parametrize("transform", [True, False])
async def test_get_list_empty_results(
    mock_get: AsyncMock,
    mocker: MockerFixture,
    transform: bool,
) -> None:
    json: dict[str, list[Any]] = {"results": []}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    df = await client.get_list("2023-10-26", transform=transform)

    assert df.is_empty()


async def test_get_list_empty_results_by_transform(
    mock_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    results = [{"docID": "S100TEST"}]
    json = {"results": results}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    mock_transform_list = mocker.patch("kabukit.sources.edinet.client.transform_list")
    mock_transform_list.return_value = pl.DataFrame({"a": []})

    mock_with_date = mocker.patch("kabukit.sources.edinet.client.with_date")

    client = EdinetClient("test_key")
    df = await client.get_list("2023-10-26")

    assert_frame_equal(df, pl.DataFrame())

    mock_transform_list.assert_called_once()
    mock_with_date.assert_not_called()
