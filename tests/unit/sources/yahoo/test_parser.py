from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


def test_get_preloaded_state() -> None:
    from kabukit.sources.yahoo.parser import get_preloaded_state

    text = """\
        <script>
            window.__PRELOADED_STATE__ = {"key": "value"};
        </script>
    """
    result = get_preloaded_state(text)
    assert result == {"key": "value"}


def test_get_preloaded_state_no_tag() -> None:
    from kabukit.sources.yahoo.parser import get_preloaded_state

    text = """\
        <a>
            window.__PRELOADED_STATE__ = {"key": "value"};
        </a>
    """
    assert get_preloaded_state(text) == {}


def test_parse_quote() -> None:
    from kabukit.sources.yahoo.parser import parse_quote

    text = """\
        <script>
            window.__PRELOADED_STATE__ = {"key": "value"};
        </script>
    """
    df = parse_quote(text)
    # assert df["Code"].unique().to_list() == ["12340"]
    assert not df.is_empty()


def test_parse_quote_empty() -> None:
    from kabukit.sources.yahoo.parser import parse_quote

    df = parse_quote("")
    assert_frame_equal(df, pl.DataFrame())


@pytest.mark.parametrize(
    ("date_str", "date", "time"),
    [
        ("6/14", datetime.date(2024, 6, 14), datetime.time(15, 30)),
        ("6/15", datetime.date(2023, 6, 15), datetime.time(15, 30)),
        ("12:30", datetime.date(2024, 6, 14), datetime.time(12, 30)),
    ],
)
def test_parse_datetime(
    mocker: MockerFixture,
    date_str: str,
    date: datetime.date,
    time: datetime.time,
) -> None:
    from kabukit.sources.yahoo.parser import _parse_datetime

    today = datetime.date(2024, 6, 14)
    mocker.patch("kabukit.utils.datetime.today", return_value=today)
    mocker.patch("kabukit.sources.yahoo.parser.today", return_value=today)

    assert _parse_datetime(date_str) == (date, time)
