from polars import DataFrame
from polars.testing import assert_frame_equal

from kabukit.core.statements import Statements


def test_number_of_shares() -> None:
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

    result = Statements(data).number_of_shares()

    expected = DataFrame(
        {
            "Date": [1],
            "Code": [3],
            "IssuedShares": [5],
            "TreasuryShares": [7],
            "AverageOutstandingShares": [9],
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
