from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from kabukit.sources.yahoo.parser import (
    _extract_content,
    _float_or_none,
    _parse_datetime,
    get_preloaded_state,
    get_preloaded_store,
    iter_index,
    iter_performance,
    iter_press_release,
    iter_previous_price,
    iter_price,
    iter_quote,
    parse_performance,
    parse_quote,
)
from kabukit.utils.datetime import today

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


def test_get_preloaded_state() -> None:
    text = """\
        <script>
            window.__PRELOADED_STATE__ = {"key": "value"};
        </script>
    """
    result = get_preloaded_state(text)
    assert result == {"key": "value"}


def test_get_preloaded_state_no_tag() -> None:
    text = """\
        <a>
            window.__PRELOADED_STATE__ = {"key": "value"};
        </a>
    """
    assert get_preloaded_state(text) == {}


def test_parse_quote(mocker: MockerFixture) -> None:
    mock_iter_quote = mocker.patch(
        "kabukit.sources.yahoo.parser.iter_quote",
        return_value=iter([("a", 1), ("b", 2)]),
    )
    text = """\
        <script>
            window.__PRELOADED_STATE__ = {"key": "value"};
        </script>
    """
    df = parse_quote(text)
    assert_frame_equal(df, pl.DataFrame({"a": 1, "b": 2}))
    mock_iter_quote.assert_called_once_with({"key": "value"})


def test_parse_quote_empty() -> None:
    df = parse_quote("")
    assert_frame_equal(df, pl.DataFrame())


def test_iter_quote(mocker: MockerFixture) -> None:
    iters = [
        mocker.patch(f"kabukit.sources.yahoo.parser.iter_{name}")
        for name in ["price", "previous_price", "index", "press_release", "performance"]
    ]
    list(iter_quote({"key": "value"}))
    for iter_func in iters:
        iter_func.assert_called_once_with({"key": "value"})


def test_iter_price() -> None:
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


def test_iter_performance_none() -> None:
    state = {"stockPerformance": {"a": 1}}

    results = list(iter_performance(state))
    assert results == [
        ("PerformanceSummary", None),
        ("PerformancePotential", None),
        ("PerformanceStability", None),
        ("PerformanceProfitability", None),
        ("PerformanceDate", None),
        ("PerformanceTime", None),
    ]


def test_get_preloaded_store() -> None:
    text = r"""<script>\"preloadedStore\":{\"key\":\"value\"}</script>"""
    result = get_preloaded_store(text)
    assert result == {"key": "value"}


def test_get_preloaded_store_empty() -> None:
    assert get_preloaded_store("<script></script>") == {}


def test_parse_performance(mocker: MockerFixture) -> None:
    mock_get_preloaded_store = mocker.patch(
        "kabukit.sources.yahoo.parser.get_preloaded_store",
        return_value={"performance": {"performance": {"a": 1, "b": 2}}},
    )

    df = parse_performance("abc")

    assert_frame_equal(df, pl.DataFrame({"a": 1, "b": 2}))
    mock_get_preloaded_store.assert_called_once_with("abc")


def test_parse_performance_empty(mocker: MockerFixture) -> None:
    mock_get_preloaded_store = mocker.patch(
        "kabukit.sources.yahoo.parser.get_preloaded_store",
        return_value={},
    )

    df = parse_performance("abc")

    assert_frame_equal(df, pl.DataFrame())
    mock_get_preloaded_store.assert_called_once_with("abc")


@pytest.mark.parametrize(
    ("value", "expected"),
    [("1", 1.0), ("1,234.5", 1234.5), ("---", None)],
)
def test_float_or_none(value: str, expected: float | None) -> None:
    assert _float_or_none(value) == expected


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
    today = datetime.date(2024, 6, 14)
    mocker.patch("kabukit.utils.datetime.today", return_value=today)
    mocker.patch("kabukit.sources.yahoo.parser.today", return_value=today)

    assert _parse_datetime(date_str) == (date, time)


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("", ""),
        ("{", ""),
        ("{a}", "{a}"),
        ("{a{b}}", "{a{b}}"),
    ],
)
def test_extract_content(content: str, expected: str) -> None:
    assert _extract_content(content) == expected
