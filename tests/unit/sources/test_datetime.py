from __future__ import annotations

import polars as pl
import pytest

pytestmark = pytest.mark.unit


def test_with_date() -> None:
    from datetime import date, time

    from kabukit.sources.datetime import _with_date

    df = pl.DataFrame(
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
                time(15, 15),
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

    df = _with_date(df, holidays=holidays)
    assert df.columns == ["Date", "DisclosedDate", "DisclosedTime", "EPS"]
    x = df["Date"].to_list()
    assert x[0] == date(2025, 1, 6)
    assert x[1] == date(2025, 1, 6)
    assert x[2] == date(2025, 1, 10)
    assert x[3] == date(2025, 1, 14)
    assert x[4] == date(2025, 1, 14)
