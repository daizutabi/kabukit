from __future__ import annotations

from typing import TYPE_CHECKING, Any

import polars as pl
import pytest
from httpx import Response

from kabukit.sources.jquants.client import JQuantsClient

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_prices(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"daily_quotes": [{"Open": 100}, {"Open": 200}]}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_prices("123", clean=False)
    assert df["Open"].to_list() == [100, 200]
    df = await client.get_latest_available_prices(clean=False)
    assert df["Open"].to_list() == [100, 200]
    df = await client.get_prices(clean=False)
    assert df["Open"].to_list() == [100, 200]


@pytest.mark.asyncio
async def test_empty(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json: dict[str, list[dict[str, str]]] = {"daily_quotes": []}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_prices("123")
    assert df.is_empty()
    df = await client.get_latest_available_prices()
    assert df.is_empty()


@pytest.mark.asyncio
async def test_error(client: JQuantsClient) -> None:
    with pytest.raises(ValueError, match="dateとfrom/to"):
        await client.get_prices(code="7203", date="2025-08-18", to="2025-08-16")


@pytest.fixture
def df() -> pl.DataFrame:
    from kabukit.sources.jquants.clean.prices import clean

    return pl.DataFrame(
        {
            "Date": ["2023-01-01", "2023-01-02"],
            "Code": ["1300", "1301"],
            "Open": [1, 2],
            "High": [3, 4],
            "Low": [5, 6],
            "Close": [7, 8],
            "UpperLimit": ["1", "0"],
            "LowerLimit": ["0", "1"],
            "Volume": [9, 10],
            "TurnoverValue": [11, 12],
            "AdjustmentFactor": [13, 14],
            "AdjustmentOpen": [15, 16],
            "AdjustmentHigh": [17, 18],
            "AdjustmentLow": [19, 20],
            "AdjustmentClose": [21, 22],
            "AdjustmentVolume": [23, 24],
        },
    ).pipe(clean)


def test_clean_shape(df: pl.DataFrame) -> None:
    assert df.shape == (2, 16)


def test_clean_date(df: pl.DataFrame) -> None:
    assert df["Date"].dtype == pl.Date


@pytest.mark.parametrize(
    ("column", "values"),
    [
        ("Open", [15, 16]),
        ("High", [17, 18]),
        ("Low", [19, 20]),
        ("Close", [21, 22]),
        ("UpperLimit", [True, False]),
        ("LowerLimit", [False, True]),
        ("Volume", [23, 24]),
        ("TurnoverValue", [11, 12]),
        ("AdjustmentFactor", [13, 14]),
        ("RawOpen", [1, 2]),
        ("RawHigh", [3, 4]),
        ("RawLow", [5, 6]),
        ("RawClose", [7, 8]),
        ("RawVolume", [9, 10]),
    ],
)
def test_clean(df: pl.DataFrame, column: str, values: list[Any]) -> None:
    assert df[column].to_list() == values
