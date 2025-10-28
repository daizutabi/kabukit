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


async def test_get_calendar(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    """Test get_calendar method."""
    # 1. Mock the API response
    json_data = {
        "trading_calendar": [
            {"Date": "2025-10-06", "HolidayDivision": "1"},  # Monday, business day
            {"Date": "2025-10-11", "HolidayDivision": "0"},  # Saturday, holiday
            {"Date": "2025-10-12", "HolidayDivision": "0"},  # Sunday, holiday
            {"Date": "2025-10-13", "HolidayDivision": "2"},  # Holiday, non-business
        ],
    }
    response = Response(200, json=json_data)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    # 2. Call the method
    client = JQuantsClient("test_token")
    result_df = await client.get_calendar()

    # 3. Assert the result
    expected_df = (
        pl.DataFrame(
            {
                "Date": [
                    datetime.date(2025, 10, 6),
                    datetime.date(2025, 10, 11),
                    datetime.date(2025, 10, 12),
                    datetime.date(2025, 10, 13),
                ],
                "HolidayDivision": [
                    "1",
                    "0",
                    "0",
                    "2",
                ],
                "IsHoliday": [
                    False,
                    True,
                    True,
                    True,
                ],
            },
        )
        .with_columns(pl.col("HolidayDivision").cast(pl.Categorical))
        .sort("Date")
    )

    assert_frame_equal(result_df.sort("Date"), expected_df)
    mock_get.assert_awaited_once_with("/markets/trading_calendar", params={})


async def test_get_calendar_empty(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    """Test get_calendar method with an empty response."""
    # 1. Mock the API response
    json: dict[str, list[dict[str, str]]] = {"trading_calendar": []}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    # 2. Call the method
    client = JQuantsClient("test_token")
    result_df = await client.get_calendar()

    # 3. Assert the result
    assert result_df.is_empty()
    mock_get.assert_awaited_once_with("/markets/trading_calendar", params={})
