from polars import DataFrame
from polars.testing import assert_frame_equal

from kabukit.core.statements import Statements


def test_shares() -> None:
    data = DataFrame(
        {
            "Date": [1, 2],
            "Code": [3, 4],
            "IssuedShares": [5, None],
            "AverageOutstandingShares": [9, 10],
            "OtherColumn": ["a", "b"],
            "TreasuryShares": [7, 8],
        },
    )

    result = Statements(data).shares()

    expected = DataFrame(
        {
            "Date": [1],
            "Code": [3],
            "IssuedShares": [5],
            "TreasuryShares": [7],
        },
    )

    assert_frame_equal(result, expected)


def test_forecast_profit() -> None:
    data = DataFrame(
        {
            "Date": [1, 2, 1, 2],
            "Code": [1, 1, 2, 2],
            "TypeOfDocument": ["FY", "1Q", "FY", "1Q"],
            "ForecastProfit": [100, 200, 300, 400],
            "NextYearForecastProfit": [None, 600, 700, 800],
        },
    )

    result = Statements(data).forecast_profit()

    expected = DataFrame(
        {
            "Date": [2, 1, 2],
            "Code": [1, 2, 2],
            "ForecastProfit": [200, 700, 400],
        },
    )

    assert_frame_equal(result, expected)


def test_forecast_dividend() -> None:
    data = DataFrame(
        {
            "Date": [1, 2, 3, 4, 5],
            "Code": [1, 1, 2, 2, 3],
            "TypeOfDocument": ["FY", "1Q", "FY", "1Q", "FY"],
            "ForecastProfit": [1000.0, 500.0, 1200.0, 600.0, 1400.0],
            "ForecastEarningsPerShare": [10.0, 5.0, 12.0, 6.0, 14.0],
            "NextYearForecastProfit": [1000.0, None, 1200.0, None, 1400.0],
            "NextYearForecastEarningsPerShare": [10.0, None, 12.0, None, None],
            "ForecastDividendPerShareAnnual": [5.0, 2.0, 6.0, 3.0, 7.0],
            "NextYearForecastDividendPerShareAnnual": [5.0, None, 6.0, None, 7.0],
        },
    )

    result = Statements(data).forecast_dividend()

    expected = DataFrame(
        {
            "Date": [1, 2, 3, 4],
            "Code": [1, 1, 2, 2],
            "ForecastDividend": [500.0, 200.0, 600.0, 300.0],
        },
    )

    assert_frame_equal(result, expected)


def test_equity() -> None:
    data = DataFrame(
        {
            "Date": [1, 2, 1],
            "Code": ["A", "A", "B"],
            "Equity": [100.0, None, 200.0],
            "OtherColumn": ["X", "Y", "Z"],
        },
    )

    result = Statements(data).equity()

    expected = DataFrame(
        {
            "Date": [1, 1],
            "Code": ["A", "B"],
            "Equity": [100.0, 200.0],
        },
    )

    assert_frame_equal(result.sort("Code"), expected)
