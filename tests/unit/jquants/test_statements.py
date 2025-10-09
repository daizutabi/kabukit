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
