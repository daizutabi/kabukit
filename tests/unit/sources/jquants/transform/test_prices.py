from __future__ import annotations

from typing import Any

import polars as pl
import pytest

from kabukit.sources.jquants.transform.prices import transform

pytestmark = pytest.mark.unit


@pytest.fixture
def df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "Date": ["2023-01-01", "2023-01-02"],
            "Code": ["1300", "1301"],
            "Open": [1, 2],
            "High": [3, 4],
            "Low": [5, 6],
            "Close": [7, 8],
            "UpperLimit": ["1", "0"],
            "LowerLimit": ["0", "1"],
            "Volume": [9, 10],
            "TurnoverValue": [11, 12],
            "AdjustmentFactor": [13, 14],
            "AdjustmentOpen": [15, 16],
            "AdjustmentHigh": [17, 18],
            "AdjustmentLow": [19, 20],
            "AdjustmentClose": [21, 22],
            "AdjustmentVolume": [23, 24],
        },
    ).pipe(transform)


def test_transform_shape(df: pl.DataFrame) -> None:
    assert df.shape == (2, 16)


def test_transform_date(df: pl.DataFrame) -> None:
    assert df["Date"].dtype == pl.Date


@pytest.mark.parametrize(
    ("column", "values"),
    [
        ("Open", [15, 16]),
        ("High", [17, 18]),
        ("Low", [19, 20]),
        ("Close", [21, 22]),
        ("UpperLimit", [True, False]),
        ("LowerLimit", [False, True]),
        ("Volume", [23, 24]),
        ("TurnoverValue", [11, 12]),
        ("AdjustmentFactor", [13, 14]),
        ("RawOpen", [1, 2]),
        ("RawHigh", [3, 4]),
        ("RawLow", [5, 6]),
        ("RawClose", [7, 8]),
        ("RawVolume", [9, 10]),
    ],
)
def test_transform(df: pl.DataFrame, column: str, values: list[Any]) -> None:
    assert df[column].to_list() == values
