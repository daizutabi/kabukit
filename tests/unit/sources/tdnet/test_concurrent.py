from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from kabukit.sources.tdnet import concurrent
from kabukit.sources.tdnet.client import TdnetClient

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


async def test_get_list_single_date(mocker: MockerFixture) -> None:
    mock_df = pl.DataFrame({"Code": [1], "Date": [datetime.date(2023, 1, 1)]})
    mock_get_list_method = mocker.AsyncMock(return_value=mock_df)
    mocker.patch.object(TdnetClient, "get_list", new=mock_get_list_method)

    result = await concurrent.get_list(datetime.date(2023, 1, 1))

    mock_get_list_method.assert_awaited_once_with(datetime.date(2023, 1, 1))
    assert_frame_equal(result, mock_df)


async def test_get_list_multiple_dates(mocker: MockerFixture) -> None:
    dates = [datetime.date(2023, 1, 1), datetime.date(2023, 1, 2)]
    mock_df_concat = pl.DataFrame(
        {
            "Code": [1, 2],
            "Date": [datetime.date(2023, 1, 1), datetime.date(2023, 1, 2)],
        },
    )
    mock_concurrent_get = mocker.AsyncMock(return_value=mock_df_concat)
    mocker.patch(
        "kabukit.sources.tdnet.concurrent.gather.get",
        new=mock_concurrent_get,
    )

    result = await concurrent.get_list(dates)

    mock_concurrent_get.assert_awaited_once_with(
        TdnetClient,
        "list",
        dates,
        max_items=None,
        max_concurrency=None,
        progress=None,
        callback=None,
    )
    assert_frame_equal(result, mock_df_concat.sort("Code", "Date"))


async def test_get_list_no_dates_specified(mocker: MockerFixture) -> None:
    available_dates = [datetime.date(2023, 1, 1), datetime.date(2023, 1, 2)]
    mock_get_dates_method = mocker.AsyncMock(return_value=available_dates)
    mocker.patch.object(TdnetClient, "get_dates", new=mock_get_dates_method)

    mock_df_concat = pl.DataFrame(
        {
            "Code": [1, 2],
            "Date": [datetime.date(2023, 1, 1), datetime.date(2023, 1, 2)],
        },
    )
    mock_concurrent_get = mocker.AsyncMock(return_value=mock_df_concat)
    mocker.patch(
        "kabukit.sources.tdnet.concurrent.gather.get",
        new=mock_concurrent_get,
    )

    result = await concurrent.get_list(None)

    mock_get_dates_method.assert_awaited_once()
    mock_concurrent_get.assert_awaited_once_with(
        TdnetClient,
        "list",
        available_dates,
        max_items=None,
        max_concurrency=None,
        progress=None,
        callback=None,
    )
    assert_frame_equal(result, mock_df_concat.sort("Code", "Date"))


async def test_get_list_returns_empty_dataframe(mocker: MockerFixture) -> None:
    mock_concurrent_get = mocker.AsyncMock(return_value=pl.DataFrame())
    mocker.patch(
        "kabukit.sources.tdnet.concurrent.gather.get",
        new=mock_concurrent_get,
    )

    result = await concurrent.get_list([datetime.date(2023, 1, 1)])

    assert result.is_empty()
    assert_frame_equal(result, pl.DataFrame())
