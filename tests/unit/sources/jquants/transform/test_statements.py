from __future__ import annotations

from typing import Any

import polars as pl
import pytest

pytestmark = pytest.mark.unit


@pytest.fixture
def df() -> pl.DataFrame:
    from kabukit.sources.jquants.transform.statements import transform

    return pl.DataFrame(
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
    ).pipe(transform)


def test_transform_shape(df: pl.DataFrame) -> None:
    assert df.shape == (3, 9)


def test_transform_disclosed_date(df: pl.DataFrame) -> None:
    assert df["DisclosedDate"].dtype == pl.Date


def test_transform_disclosed_time(df: pl.DataFrame) -> None:
    assert df["DisclosedTime"].dtype == pl.Time


def test_transform_current_period(df: pl.DataFrame) -> None:
    assert df["TypeOfCurrentPeriod"].dtype == pl.Categorical


@pytest.mark.parametrize("column", ["ForecastProfit", "AverageOutstandingShares"])
def test_transform_float(df: pl.DataFrame, column: str) -> None:
    assert df[column].dtype == pl.Float64


@pytest.mark.parametrize("column", ["IssuedShares", "TreasuryShares"])
def test_transform_int(df: pl.DataFrame, column: str) -> None:
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
def test_transform(df: pl.DataFrame, column: str, values: list[Any]) -> None:
    assert df[column].to_list() == values
