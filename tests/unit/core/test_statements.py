from polars import DataFrame
from polars.testing import assert_frame_equal

from kabukit.core.statements import Statements


def test_number_of_shares() -> None:
    data = DataFrame(
        {
            "Date": [1, 2],
            "Code": [3, 4],
            "NumberOfShares": [5, None],
            "AverageNumberOfShares": [9, 10],
            "OtherColumn": ["a", "b"],
            "NumberOfTreasuryStock": [7, 8],
        },
    )
    statements = Statements(data)

    df = statements.number_of_shares()

    expected = DataFrame(
        {
            "Date": [1],
            "Code": [3],
            "NumberOfShares": [5],
            "NumberOfTreasuryStock": [7],
            "AverageNumberOfShares": [9],
        },
    )

    assert_frame_equal(df, expected)
