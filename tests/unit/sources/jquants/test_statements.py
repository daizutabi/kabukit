from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any

import polars as pl
import pytest
from httpx import Response
from polars import DataFrame

from kabukit.sources.jquants.client import JQuantsClient

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_statements(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"statements": [{"Profit": 100}, {"Profit": 200}]}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_statements("123", clean=False)
    assert df["Profit"].to_list() == [100, 200]


@pytest.mark.asyncio
async def test_empty(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json: dict[str, list[dict[str, str]]] = {"statements": []}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_statements("123")
    assert df.is_empty()


@pytest.mark.asyncio
async def test_error(client: JQuantsClient) -> None:
    with pytest.raises(ValueError, match="codeまたはdate"):
        await client.get_statements()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("clean_flag", "with_date_flag", "clean_called", "with_date_called"),
    [
        (True, True, True, True),
        (True, False, True, False),
        (False, True, False, False),
        (False, False, False, False),
    ],
)
async def test_get_flags(
    mock_get: AsyncMock,
    mocker: MockerFixture,
    clean_flag: bool,
    with_date_flag: bool,
    clean_called: bool,
    with_date_called: bool,
) -> None:
    """Test the clean and with_date flags in get_statements."""

    def get_side_effect(url: str, params: dict[str, Any] | None = None) -> Response:  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
        if "statements" in url:
            json = {
                "statements": [
                    {"LocalCode": "7203", "DisclosedDate": "2023-01-05"},
                ],
            }
            response = Response(200, json=json)
        elif "trading_calendar" in url:
            json = {
                "trading_calendar": [
                    {"Date": "2023-01-03", "HolidayDivision": "0"},
                ],
            }
            response = Response(200, json=json)
        else:
            response = Response(404)
        response.raise_for_status = mocker.MagicMock()
        return response

    mock_get.side_effect = get_side_effect

    mock_clean = mocker.patch(
        "kabukit.sources.jquants.statements.clean",
        return_value=DataFrame(
            {
                "Code": ["7203"],
                "DisclosedDate": [datetime.date(2023, 1, 5)],
                "DisclosedTime": [datetime.time(9, 0)],
            },
        ),
    )
    mock_with_date = mocker.patch(
        "kabukit.sources.jquants.statements.with_date",
        return_value=DataFrame({"Date": [datetime.date(2023, 1, 1)]}),
    )

    client = JQuantsClient("test_token")
    await client.get_statements(
        code="7203",
        clean=clean_flag,
        with_date=with_date_flag,
    )

    if clean_called:
        mock_clean.assert_called_once()
    else:
        mock_clean.assert_not_called()

    if with_date_called:
        mock_with_date.assert_called_once()
    else:
        mock_with_date.assert_not_called()


@pytest.fixture
def df() -> DataFrame:
    from kabukit.sources.jquants.statements import clean

    return DataFrame(
        {
            "DisclosedDate": ["2023-01-01", "2023-01-20", "2023-01-30"],
            "DisclosedTime": ["09:00", "15:30", "12:00"],
            "LocalCode": ["1300", "1301", "1302"],
            "NumberOfIssuedAndOutstandingSharesAtTheEndOfFiscalYearIncludingTreasuryStock": [  # noqa: E501
                "1",
                "2",
                "3",
            ],
            "NumberOfTreasuryStockAtTheEndOfFiscalYear": ["4", "5", "6"],
            "AverageNumberOfShares": ["7.1", "8.2", "9.3"],
            "TypeOfCurrentPeriod": ["A", "B", "C"],
            "RetrospectiveRestatement": ["true", "false", ""],
            "ForecastProfit": ["1.0", "2.0", ""],
        },
    ).pipe(clean)


def test_clean_shape(df: DataFrame) -> None:
    assert df.shape == (3, 9)


def test_clean_disclosed_date(df: DataFrame) -> None:
    assert df["DisclosedDate"].dtype == pl.Date


def test_clean_disclosed_time(df: DataFrame) -> None:
    assert df["DisclosedTime"].dtype == pl.Time


def test_clean_current_period(df: DataFrame) -> None:
    assert df["TypeOfCurrentPeriod"].dtype == pl.Categorical


@pytest.mark.parametrize("column", ["ForecastProfit", "AverageOutstandingShares"])
def test_clean_float(df: DataFrame, column: str) -> None:
    assert df[column].dtype == pl.Float64


@pytest.mark.parametrize("column", ["IssuedShares", "TreasuryShares"])
def test_clean_int(df: DataFrame, column: str) -> None:
    assert df[column].dtype == pl.Int64


@pytest.mark.parametrize(
    ("column", "values"),
    [
        ("IssuedShares", [1, 2, 3]),
        ("TreasuryShares", [4, 5, 6]),
        ("AverageOutstandingShares", [7.1, 8.2, 9.3]),
        ("ForecastProfit", [1.0, 2.0, None]),
        ("RetrospectiveRestatement", [True, False, None]),
    ],
)
def test_clean(df: DataFrame, column: str, values: list[Any]) -> None:
    assert df[column].to_list() == values


def test_with_date() -> None:
    from datetime import date, time

    from kabukit.sources.jquants.statements import with_date

    df = DataFrame(
        {
            "DisclosedDate": [
                date(2025, 1, 4),
                date(2025, 1, 4),
                date(2025, 1, 10),
                date(2025, 1, 10),
                date(2025, 1, 10),
            ],
            "DisclosedTime": [
                time(9, 0),
                time(16, 0),
                time(15, 15),
                time(15, 30),
                None,
            ],
            "EPS": [1, 2, 3, 4, 5],
        },
    )

    holidays = [
        date(2025, 1, 1),
        date(2025, 1, 4),
        date(2025, 1, 5),
        date(2025, 1, 11),
        date(2025, 1, 12),
        date(2025, 1, 13),
    ]

    df = with_date(df, holidays=holidays)
    assert df.columns == ["Date", "DisclosedDate", "DisclosedTime", "EPS"]
    x = df["Date"].to_list()
    assert x[0] == date(2025, 1, 6)
    assert x[1] == date(2025, 1, 6)
    assert x[2] == date(2025, 1, 10)
    assert x[3] == date(2025, 1, 14)
    assert x[4] == date(2025, 1, 14)
