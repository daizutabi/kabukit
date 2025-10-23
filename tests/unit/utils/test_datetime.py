from __future__ import annotations

import datetime

import pytest

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("date_str", "fmt", "date"),
    [
        ("2023-10-15", "%Y-%m-%d", datetime.date(2023, 10, 15)),
        ("2023-10-15", None, datetime.date(2023, 10, 15)),
        ("20231015", "%Y%m%d", datetime.date(2023, 10, 15)),
        ("20231015", None, datetime.date(2023, 10, 15)),
    ],
)
def test_strpdate(date_str: str, fmt: str | None, date: datetime.date) -> None:
    from kabukit.utils.datetime import strpdate

    assert strpdate(date_str, fmt) == date


@pytest.mark.parametrize(
    ("time_str", "fmt", "date"),
    [
        ("01:01", "%H:%M", datetime.time(1, 1, 0)),
        ("23:49", None, datetime.time(23, 49, 0)),
        ("1030", "%H%M", datetime.time(10, 30, 0)),
    ],
)
def test_strptime(time_str: str, fmt: str | None, date: datetime.date) -> None:
    from kabukit.utils.datetime import strptime

    assert strptime(time_str, fmt) == date


def test_dates_days() -> None:
    from kabukit.utils.datetime import get_dates

    assert len(get_dates(days=5)) == 5


def test_dates_years() -> None:
    from kabukit.utils.datetime import get_dates

    assert len(get_dates(years=1)) in [365, 366]
    assert len(get_dates(years=2)) in [365 + 365, 366 + 365]
    assert len(get_dates(years=4)) == 365 * 4 + 1


def test_dates_error() -> None:
    from kabukit.utils.datetime import get_dates

    with pytest.raises(ValueError, match="daysまたはyears"):
        get_dates()
