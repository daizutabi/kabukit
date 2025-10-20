from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars import DataFrame, Series
from polars.testing import assert_frame_equal

from kabukit.core.prices import Prices
from kabukit.core.statements import Statements

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


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
                "ReportDate",
                [
                    date(2023, 3, 31),
                    date(2023, 6, 30),
                    date(2023, 6, 30),
                    None,
                    date(2023, 4, 30),
                    date(2023, 4, 30),
                ],
                dtype=pl.Date,
            ),
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


def test_with_market_cap() -> None:
    prices_df = DataFrame(
        {
            "Date": [
                date(2023, 1, 1),
                date(2023, 1, 2),
                date(2023, 1, 3),
            ],
            "Code": ["A", "A", "A"],
            "RawClose": [100.0, 110.0, 120.0],
            "AdjustedIssuedShares": [1000, 1000, 2000],
            "AdjustedTreasuryShares": [100, 100, 200],
        },
    )

    prices = Prices(prices_df)

    result = prices.with_market_cap()

    expected = prices_df.with_columns(
        Series("MarketCap", [90000.0, 99000.0, 216000.0]),
    )

    assert_frame_equal(result.data, expected)


def test_with_equity() -> None:
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
                date(2023, 3, 31),
                date(2023, 6, 30),
                date(2023, 3, 31),
            ],
            "Code": ["A", "A", "B"],
            "Equity": [1000.0, 1200.0, 2000.0],
        },
    )

    prices = Prices(prices_df)
    statements = Statements(statements_df)

    result = prices.with_equity(statements)

    expected = prices_df.with_columns(
        Series("Equity", [1000.0, 1000.0, 1000.0, None, 2000.0], dtype=pl.Float64),
    )

    assert_frame_equal(result.data, expected)


def test_with_book_value_yield() -> None:
    prices_df = DataFrame(
        {
            "Date": [date(2023, 1, 1), date(2023, 1, 2)],
            "Code": ["A", "A"],
            "RawClose": [1000.0, 1250.0],
            "Equity": [1000000.0, 1000000.0],
            "AdjustedIssuedShares": [1000, 1000],
            "AdjustedTreasuryShares": [100, 100],
        },
    )

    prices = Prices(prices_df)

    result = prices.with_book_value_yield()

    expected = prices_df.with_columns(
        [
            Series("BookValuePerShare", [1111.11, 1111.11]),
            Series("BookValueYield", [1.1111, 0.8889]),
        ],
    )

    assert_frame_equal(result.data, expected, check_exact=False, rel_tol=1e-4)


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


def test_with_earnings_yield() -> None:
    prices_df = DataFrame(
        {
            "Date": [date(2023, 1, 1), date(2023, 1, 2)],
            "Code": ["A", "A"],
            "RawClose": [2000.0, 1800.0],
            "ForecastProfit": [100000.0, 100000.0],
            "AdjustedIssuedShares": [1000, 1000],
            "AdjustedTreasuryShares": [100, 100],
        },
    )

    prices = Prices(prices_df)

    result = prices.with_earnings_yield()

    expected = prices_df.with_columns(
        [
            Series("EarningsPerShare", [111.1111, 111.1111]),
            Series("EarningsYield", [0.055556, 0.061728]),
        ],
    )

    assert_frame_equal(result.data, expected, check_exact=False, rel_tol=1e-4)


def test_with_forecast_dividend() -> None:
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
    ).sort("Code", "Date")

    statements_df = DataFrame(
        {
            "Date": [
                date(2023, 5, 1),
                date(2023, 6, 1),
                date(2023, 4, 1),
            ],
            "Code": ["A", "A", "B"],
            "TypeOfDocument": ["1Q", "1Q", "FY"],
            "ForecastProfit": [1000.0, 1500.0, None],
            "ForecastEarningsPerShare": [10.0, 10.0, None],
            "NextYearForecastProfit": [None, None, 2000.0],
            "NextYearForecastEarningsPerShare": [None, None, 10.0],
            "ForecastDividendPerShareAnnual": [5.0, 6.0, None],
            "NextYearForecastDividendPerShareAnnual": [None, None, 10.0],
        },
    )

    prices = Prices(prices_df)
    statements = Statements(statements_df)

    result = prices.with_forecast_dividend(statements)

    expected = prices_df.with_columns(
        Series("ForecastDividend", [None, 500.0, 900.0, None, 2000.0]),
    )

    assert_frame_equal(result.data, expected)


def test_with_dividend_yield() -> None:
    prices_df = DataFrame(
        {
            "Date": [date(2023, 1, 1), date(2023, 1, 2)],
            "Code": ["A", "A"],
            "RawClose": [1000.0, 1100.0],
            "ForecastDividend": [45000.0, 45000.0],
            "AdjustedIssuedShares": [1000, 1000],
            "AdjustedTreasuryShares": [100, 100],
        },
    )

    prices = Prices(prices_df)

    result = prices.with_dividend_yield()

    expected = prices_df.with_columns(
        [
            Series("DividendPerShare", [50.0, 50.0]),
            Series("DividendYield", [0.05, 0.04545454]),
        ],
    )

    assert_frame_equal(result.data, expected, check_exact=False, rel_tol=1e-4)


@pytest.mark.parametrize(
    ("prices_method_name", "statements_method_name", "statements_return_cols"),
    [
        (
            "with_adjusted_shares",
            "shares",
            ["Date", "Code", "IssuedShares", "TreasuryShares"],
        ),
        ("with_equity", "equity", ["Date", "Code", "Equity"]),
        ("with_forecast_profit", "forecast_profit", ["Date", "Code", "ForecastProfit"]),
        (
            "with_forecast_dividend",
            "forecast_dividend",
            ["Date", "Code", "ForecastDividend"],
        ),
    ],
)
def test_data_loading_methods_are_idempotent(
    mocker: MockerFixture,
    prices_method_name: str,
    statements_method_name: str,
    statements_return_cols: list[str],
) -> None:
    """データロードメソッドがべき等であることを検証する"""
    prices_df = DataFrame(
        {
            "Date": [date(2023, 1, 1)],
            "Code": ["A"],
            "RawClose": [100.0],
            "AdjustmentFactor": [1.0],
        },
    )
    prices = Prices(prices_df)

    statements = Statements(DataFrame({"Date": [date(2023, 1, 1)], "Code": ["A"]}))

    mock_data = {}
    for col in statements_return_cols:
        if col == "Date":
            mock_data[col] = [date(2023, 1, 1)]
        elif col == "Code":
            mock_data[col] = ["A"]
        else:
            mock_data[col] = [1.0]  # その他のデータカラムはfloat

    mock_return_df = DataFrame(mock_data)

    mocker.patch.object(
        statements,
        statements_method_name,
        return_value=mock_return_df,
    )
    spy = mocker.spy(
        statements,
        statements_method_name,
    )  # モックされたメソッドをスパイする

    method = getattr(prices, prices_method_name)
    result1 = method(statements)  # 1回目の呼び出し
    result2 = getattr(result1, prices_method_name)(
        statements,
    )  # 1回目の結果に対して2回目の呼び出し

    assert_frame_equal(result1.data, result2.data)
    assert spy.call_count == 1


@pytest.mark.parametrize(
    "method_name",
    ["with_market_cap", "with_book_value_yield", "with_earnings_yield"],
)
def test_methods_raise_key_error_without_adjusted_shares(method_name: str) -> None:
    """前提条件となる adjusted_shares がない場合にKeyErrorを送出する"""
    prices_df = DataFrame({"Code": ["A"]})  # `Adjusted...Shares` 列を持たない
    prices = Prices(prices_df)

    method = getattr(prices, method_name)

    with pytest.raises(KeyError, match="必要な列が存在しません"):
        method()


def test_with_yields() -> None:
    prices_df = DataFrame(
        {
            "Date": [date(2023, 1, 1)],
            "Code": ["A"],
            "RawClose": [1000.0],
            "AdjustmentFactor": [1.0],
        },
    )

    statements_df = DataFrame(
        {
            "Date": [date(2023, 1, 1)],
            "Code": ["A"],
            "IssuedShares": [1000],
            "TreasuryShares": [100],
            "Equity": [900000.0],
            "ForecastProfit": [90000.0],
            "ForecastDividend": [45000.0],
            "TypeOfDocument": ["FY"],
            "NextYearForecastProfit": [90000.0],
            "ForecastEarningsPerShare": [100.0],
            "NextYearForecastEarningsPerShare": [100.0],
            "ForecastDividendPerShareAnnual": [50.0],
            "NextYearForecastDividendPerShareAnnual": [50.0],
        },
    )

    prices = Prices(prices_df)
    statements = Statements(statements_df)

    result = prices.with_yields(statements)

    expected_df = prices_df.with_columns(
        [
            Series("ReportDate", [date(2023, 1, 1)], dtype=pl.Date),
            Series("AdjustedIssuedShares", [1000], dtype=pl.Int64),
            Series("AdjustedTreasuryShares", [100], dtype=pl.Int64),
            Series("Equity", [900000.0]),
            Series("BookValuePerShare", [1000.0]),
            Series("BookValueYield", [1.0]),
            Series("ForecastProfit", [90000.0]),
            Series("EarningsPerShare", [100.0]),
            Series("EarningsYield", [0.1]),
            Series("ForecastDividend", [45000.0]),
            Series("DividendPerShare", [50.0]),
            Series("DividendYield", [0.05]),
        ],
    )

    assert_frame_equal(result.data, expected_df, check_exact=False, rel_tol=1e-4)


def test_with_period_stats() -> None:
    prices_df = DataFrame(
        {
            "Date": [date(2023, 1, 1)],
            "Code": ["A"],
            "RawClose": [100.0],
            "Close": [100.0],
            "AdjustmentFactor": [1.0],
        },
    )
    statements_df = DataFrame(
        {
            "Date": [date(2023, 1, 1)],
            "Code": ["A"],
            "IssuedShares": [1000],
            "TreasuryShares": [100],
            "Equity": [90000.0],
            "ForecastProfit": [9000.0],
            "ForecastDividend": [4500.0],
            "TypeOfDocument": ["FY"],
            "NextYearForecastProfit": [90000.0],
            "ForecastEarningsPerShare": [100.0],
            "NextYearForecastEarningsPerShare": [100.0],
            "ForecastDividendPerShareAnnual": [50.0],
            "NextYearForecastDividendPerShareAnnual": [50.0],
        },
    )

    prices = Prices(prices_df)
    statements = Statements(statements_df)
    processed_prices = prices.with_yields(statements)

    result = processed_prices.with_period_stats()

    expected_df = processed_prices.data.with_columns(
        [
            Series("BookValueYield_PeriodOpen", [1.0]),
            Series("BookValueYield_PeriodHigh", [1.0]),
            Series("BookValueYield_PeriodLow", [1.0]),
            Series("BookValueYield_PeriodClose", [1.0]),
            Series("BookValueYield_PeriodMean", [1.0]),
            Series("EarningsYield_PeriodOpen", [1.0]),
            Series("EarningsYield_PeriodHigh", [1.0]),
            Series("EarningsYield_PeriodLow", [1.0]),
            Series("EarningsYield_PeriodClose", [1.0]),
            Series("EarningsYield_PeriodMean", [1.0]),
            Series("DividendYield_PeriodOpen", [0.5]),
            Series("DividendYield_PeriodHigh", [0.5]),
            Series("DividendYield_PeriodLow", [0.5]),
            Series("DividendYield_PeriodClose", [0.5]),
            Series("DividendYield_PeriodMean", [0.5]),
            Series("Close_PeriodOpen", [100.0]),
            Series("Close_PeriodHigh", [100.0]),
            Series("Close_PeriodLow", [100.0]),
            Series("Close_PeriodClose", [100.0]),
            Series("Close_PeriodMean", [100.0]),
        ],
    )

    assert_frame_equal(result.data, expected_df, check_exact=False, rel_tol=1e-4)


def test_period_stats_raise_key_error_without_required_columns() -> None:
    prices = Prices(DataFrame({"Code": ["A"]}))
    with pytest.raises(KeyError, match="必要な列が存在しません"):
        prices.with_period_stats()
