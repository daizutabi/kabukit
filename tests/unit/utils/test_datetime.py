from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

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
def test_parse_date(date_str: str, fmt: str | None, date: datetime.date) -> None:
    from kabukit.utils.datetime import parse_date

    assert parse_date(date_str, fmt) == date


def test_parse_month_day(mocker: MockerFixture) -> None:
    from kabukit.utils.datetime import parse_month_day

    mocker.patch(
        "kabukit.utils.datetime.today",
        return_value=datetime.date(2024, 6, 15),
    )

    assert parse_month_day("6/14") == datetime.date(2024, 6, 14)
    assert parse_month_day("6/15") == datetime.date(2024, 6, 15)
    assert parse_month_day("6/16") == datetime.date(2023, 6, 16)


@pytest.mark.parametrize(
    ("time_str", "fmt", "time"),
    [
        ("01:01", "%H:%M", datetime.time(1, 1, 0)),
        ("23:49", None, datetime.time(23, 49, 0)),
        ("1030", "%H%M", datetime.time(10, 30, 0)),
    ],
)
def test_parse_time(time_str: str, fmt: str | None, time: datetime.time) -> None:
    from kabukit.utils.datetime import parse_time

    assert parse_time(time_str, fmt) == time


def test_today_date() -> None:
    from kabukit.utils.datetime import today

    assert isinstance(today(), datetime.date)


def test_today_str() -> None:
    from kabukit.utils.datetime import today

    assert isinstance(today(as_str=True), str)


def test_get_past_dates_days() -> None:
    from kabukit.utils.datetime import get_past_dates

    assert len(get_past_dates(days=5)) == 5


def test_get_past_dates_years() -> None:
    from kabukit.utils.datetime import get_past_dates

    assert len(get_past_dates(years=1)) in [365, 366]
    assert len(get_past_dates(years=2)) in [365 + 365, 366 + 365]
    assert len(get_past_dates(years=4)) == 365 * 4 + 1


def test_get_past_dates_error() -> None:
    from kabukit.utils.datetime import get_past_dates

    with pytest.raises(ValueError, match="daysまたはyears"):
        get_past_dates()
