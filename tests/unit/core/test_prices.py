from datetime import date

import pytest
from polars import DataFrame, Series
from polars.testing import assert_frame_equal

from kabukit.core.prices import Prices


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


def test_with_relative_shares() -> None:
    source_data = DataFrame(
        {
            "Code": ["A", "A", "A", "A", "B", "B", "B", "B", "B"],
            "Date": [
                date(2023, 1, 1),
                date(2023, 1, 2),  # A: T-1
                date(2023, 1, 3),  # A: T (split)
                date(2023, 1, 4),
                date(2023, 1, 1),
                date(2023, 1, 2),  # B: T1 (split)
                date(2023, 1, 3),
                date(2023, 1, 4),  # B: T2 (split)
                date(2023, 1, 5),
            ],
            "AdjustmentFactor": [
                1.0,
                1.0,
                0.5,  # Stock A: 2:1 split
                1.0,
                1.0,
                0.5,  # Stock B: 2:1 split
                1.0,
                0.5,  # Stock B: 2:1 split again
                1.0,
            ],
        },
    )
    prices = Prices(source_data)

    result_df = prices.with_relative_shares().data

    expected_data = source_data.with_columns(
        Series(
            "RelativeShares",
            [
                0.5,  # A: before split
                0.5,  # A: before split
                1.0,  # A: after split
                1.0,  # A: after split
                0.25,  # B: before both splits
                0.5,  # B: after 1st split
                0.5,  # B: after 1st split
                1.0,  # B: after 2nd split
                1.0,  # B: after 2nd split
            ],
        ),
    )

    assert_frame_equal(result_df, expected_data)
