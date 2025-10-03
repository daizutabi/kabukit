from datetime import date

import polars as pl
import pytest
from polars import DataFrame, Series
from polars.testing import assert_frame_equal

from kabukit.core.prices import Prices
from kabukit.core.statements import Statements


@pytest.fixture(scope="module")
def data() -> DataFrame:
    return DataFrame(
        {
            "Date": [
                date(2023, 1, 1),
                date(2023, 1, 2),
                date(2023, 2, 1),
                date(2023, 2, 2),
                date(2023, 1, 1),
                date(2023, 1, 2),
                date(2023, 2, 1),
                date(2023, 2, 2),
            ],
            "Code": ["A", "A", "A", "A", "B", "B", "B", "B"],
            "Open": [101, 102, 103, 104, None, 106, 107, 108],
            "High": [111, 112, 113, None, 115, 116, 117, 118],
            "Low": [91, 92, 93, 94, 95, 96, 97, 98],
            "Close": [107, 108, 109, 110, 111, 112, 113, None],
            "Volume": [500, 1000, 600, 1100, 700, 1200, 800, 1300],
            "TurnoverValue": [1000, 2000, 1200, 2200, 1400, 2400, 1600, 2600],
        },
    )


def test_truncate_day(data: DataFrame) -> None:
    prices = Prices(data)
    df = prices.truncate("1d").data
    assert df.equals(data)


def test_truncate_month(data: DataFrame) -> None:
    prices = Prices(data)
    df = prices.truncate("1mo").data
    assert df.shape == (4, 8)
    assert df["Date"].to_list() == [
        date(2023, 1, 1),
        date(2023, 2, 1),
        date(2023, 1, 1),
        date(2023, 2, 1),
    ]
    assert df["Code"].to_list() == ["A", "A", "B", "B"]
    assert df["Open"].to_list() == [101, 103, 106, 107]
    assert df["High"].to_list() == [112, 113, 116, 118]
    assert df["Low"].to_list() == [91, 93, 95, 97]
    assert df["Close"].to_list() == [108, 110, 112, 113]
    assert df["Volume"].to_list() == [1500, 1700, 1900, 2100]
    assert df["TurnoverValue"].to_list() == [3000, 3400, 3800, 4200]


def test_with_adjusted_shares() -> None:
    prices_df = DataFrame(
        {
            "Date": [
                date(2023, 5, 1),
                date(2023, 7, 15),
                date(2023, 8, 1),
                date(2023, 2, 1),
                date(2023, 4, 30),
                date(2023, 5, 1),
            ],
            "Code": ["A", "A", "A", "B", "B", "B"],
            "AdjustmentFactor": [1.0, 0.5, 0.2, 1.0, 1.0, 2.0],
        },
    )

    statements_df = DataFrame(
        {
            "Date": [
                date(2023, 3, 31),
                date(2023, 6, 30),
                date(2023, 4, 30),
            ],
            "Code": ["A", "A", "B"],
            "IssuedShares": [1000, 1200, 2000],
            "TreasuryShares": [100, 120, 200],
            "AverageOutstandingShares": [0, 0, 0],
        },
    )

    prices = Prices(prices_df)
    statements = Statements(statements_df)

    expected = prices_df.with_columns(
        [
            Series(
                "AdjustedIssuedShares",
                [1000, 2400, 12000, None, 2000, 1000],
                dtype=pl.Int64,
            ),
            Series(
                "AdjustedTreasuryShares",
                [100, 240, 1200, None, 200, 100],
                dtype=pl.Int64,
            ),
        ],
    )

    result = prices.with_adjusted_shares(statements)

    assert_frame_equal(result.data, expected)


def test_with_forecast_profit() -> None:
    prices_df = DataFrame(
        {
            "Date": [
                date(2023, 4, 1),
                date(2023, 5, 15),
                date(2023, 6, 10),
                date(2023, 3, 10),
                date(2023, 4, 5),
            ],
            "Code": ["A", "A", "A", "B", "B"],
        },
    )

    statements_df = DataFrame(
        {
            "Date": [
                date(2023, 5, 1),
                date(2023, 6, 1),
                date(2023, 4, 1),
            ],
            "Code": ["A", "A", "B"],
            "TypeOfDocument": ["1Q", "2Q", "FY"],
            "ForecastProfit": [100.0, 150.0, None],
            "NextYearForecastProfit": [None, None, 200.0],
        },
    )

    prices = Prices(prices_df)
    statements = Statements(statements_df)

    result = prices.with_forecast_profit(statements)

    expected = prices_df.with_columns(
        Series("ForecastProfit", [None, 100.0, 150.0, None, 200.0]),
    )

    assert_frame_equal(result.data, expected)
