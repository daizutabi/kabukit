import datetime
from typing import Any

import polars as pl
import pytest
from polars import DataFrame


@pytest.fixture
def df() -> DataFrame:
    from kabukit.jquants.statements import clean

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


@pytest.mark.parametrize("column", ["TotalShares", "TreasuryShares"])
def test_clean_int(df: DataFrame, column: str) -> None:
    assert df[column].dtype == pl.Int64


@pytest.mark.parametrize(
    ("column", "values"),
    [
        ("TotalShares", [1, 2, 3]),
        ("TreasuryShares", [4, 5, 6]),
        ("AverageOutstandingShares", [7.1, 8.2, 9.3]),
        ("ForecastProfit", [1.0, 2.0, None]),
        ("RetrospectiveRestatement", [True, False, None]),
    ],
)
def test_clean(df: DataFrame, column: str, values: list[Any]) -> None:
    assert df[column].to_list() == values


def test_holidays() -> None:
    from kabukit.jquants.statements import get_holidays

    holidays = get_holidays(n=5)
    year = datetime.datetime.now().year  # noqa: DTZ005
    assert holidays[0].year == year - 5
    assert holidays[0].month == 1
    assert holidays[0].day == 1


def test_holidays_year() -> None:
    from kabukit.jquants.statements import get_holidays

    holidays = get_holidays(2000, 5)
    assert holidays[0].year == 1995
    assert holidays[0].month == 1
    assert holidays[0].day == 1


def test_with_date() -> None:
    from datetime import date, time

    from kabukit.jquants.statements import with_date

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
                time(9, 0),
                time(15, 30),
                None,
            ],
            "EPS": [1, 2, 3, 4, 5],
        },
    )

    df = with_date(df, 2025)
    assert df.columns == ["Date", "DisclosedDate", "DisclosedTime", "EPS"]
    x = df["Date"].to_list()
    assert x[0] == date(2025, 1, 6)
    assert x[1] == date(2025, 1, 6)
    assert x[2] == date(2025, 1, 10)
    assert x[3] == date(2025, 1, 14)
    assert x[4] == date(2025, 1, 14)


def test_join_asof() -> None:
    from datetime import date

    stmt = DataFrame(
        {
            "Date": [
                date(2025, 2, 3),
                date(2025, 2, 6),
            ],
            "EPS": [1, 2],
        },
    )

    price = pl.DataFrame(
        {
            "Date": [
                date(2025, 2, 1),
                date(2025, 2, 2),
                date(2025, 2, 3),
                date(2025, 2, 4),
                date(2025, 2, 5),
                date(2025, 2, 6),
                date(2025, 2, 7),
                date(2025, 2, 8),
            ],
            "Close": [3, 4, 5, 6, 7, 8, 9, 10],
        },
    )

    df = price.join_asof(stmt, on="Date", strategy="backward")
    x = df["EPS"].to_list()
    assert x == [None, None, 1, 1, 1, 2, 2, 2]
