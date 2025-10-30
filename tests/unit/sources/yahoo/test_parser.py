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


@pytest.mark.parametrize(
    ("date_str", "date", "time"),
    [
        ("6/14", datetime.date(2024, 6, 14), datetime.time(15, 30)),
        ("6/15", datetime.date(2023, 6, 15), datetime.time(15, 30)),
        ("12:30", datetime.date(2024, 6, 14), datetime.time(12, 30)),
        ("2025/10", datetime.date(2025, 10, 31), datetime.time(0, 0)),
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


def test_iter_price() -> None:
    from kabukit.sources.yahoo.parser import iter_price
    from kabukit.utils.datetime import today

    state = {
        "mainStocksPriceBoard": {
            "priceBoard": {
                "price": "1,000.5",
                "priceDateTime": "14:30",
            },
        },
    }

    results = list(iter_price(state))
    assert results == [
        ("Price", 1000.5),
        ("PriceDate", today()),
        ("PriceTime", datetime.time(14, 30)),
    ]


def test_iter_previous_price() -> None:
    from kabukit.sources.yahoo.parser import iter_previous_price
    from kabukit.utils.datetime import today

    state = {
        "mainStocksDetail": {
            "detail": {
                "previousPrice": "1,000.5",
                "previousPriceDate": "14:30",
            },
        },
    }

    results = list(iter_previous_price(state))
    assert results == [
        ("PreviousPrice", 1000.5),
        ("PreviousPriceDate", today()),
        ("PreviousPriceTime", datetime.time(14, 30)),
    ]


def test_iter_index() -> None:
    from kabukit.sources.yahoo.parser import iter_index
    from kabukit.utils.datetime import today

    state = {
        "mainStocksDetail": {
            "referenceIndex": {
                "sharesIssued": "12,345",
                "sharesIssuedDate": "10/10",
                "bps": "1,235.5",
                "bpsDate": "2020/11",
                "eps": "3.4",
                "epsDate": "2020/10",
                "dps": "1.2",
                "dpsDate": "2020/09",
            },
        },
    }

    results = list(iter_index(state))
    assert results == [
        ("IssuedShares", 12345),
        ("IssuedSharesDate", datetime.date(today().year, 10, 10)),
        ("BookValuePerShare", 1235.5),
        ("BookValuePerShareDate", datetime.date(2020, 11, 30)),
        ("EarningsPerShare", 3.4),
        ("EarningsPerShareDate", datetime.date(2020, 10, 31)),
        ("DividendPerShare", 1.2),
        ("DividendPerShareDate", datetime.date(2020, 9, 30)),
    ]


def test_iter_press_release() -> None:
    from kabukit.sources.yahoo.parser import iter_press_release

    state = {
        "mainStocksPressReleaseSummary": {
            "summary": "abc",
            "disclosedTime": "2025-08-07T14:00:00+09:00",
        },
    }

    results = list(iter_press_release(state))
    assert results == [
        ("PressReleaseSummary", "abc"),
        ("PressReleaseDate", datetime.date(2025, 8, 7)),
        ("PressReleaseTime", datetime.time(14, 0)),
    ]


def test_iter_performance() -> None:
    from kabukit.sources.yahoo.parser import iter_performance

    state = {
        "stockPerformance": {
            "summaryInfo": {
                "summary": "abc",
                "potential": 80,
                "stability": 90,
                "profitability": 70,
                "updateTime": "2024-06-14T10:00:00+09:00",
            },
        },
    }

    results = list(iter_performance(state))
    assert results == [
        ("PerformanceSummary", "abc"),
        ("PerformancePotential", 80),
        ("PerformanceStability", 90),
        ("PerformanceProfitability", 70),
        ("PerformanceDate", datetime.date(2024, 6, 14)),
        ("PerformanceTime", datetime.time(10, 0)),
    ]
