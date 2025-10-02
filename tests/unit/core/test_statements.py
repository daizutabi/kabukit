from polars import DataFrame
from polars.testing import assert_frame_equal

from kabukit.core.statements import Statements


def test_number_of_shares() -> None:
    data = DataFrame(
        {
            "Date": [1, 2],
            "Code": [3, 4],
            "TotalShares": [5, None],
            "AverageOutstandingShares": [9, 10],
            "OtherColumn": ["a", "b"],
            "TreasuryShares": [7, 8],
        },
    )
    statements = Statements(data)

    df = statements.number_of_shares()

    expected = DataFrame(
        {
            "Date": [1],
            "Code": [3],
            "TotalShares": [5],
            "TreasuryShares": [7],
            "AverageOutstandingShares": [9],
        },
    )

    assert_frame_equal(df, expected)
