from __future__ import annotations

import datetime
from typing import Any

import polars as pl
import pytest

from kabukit.sources.yahoo.parser import (
    iter_index,
    iter_performance,
    iter_press_release,
    iter_previous_price,
    iter_price,
    parse_performance,
    parse_quote,
)

pytestmark = pytest.mark.system


def test_state_iter_price(state: dict[str, Any]) -> None:
    x = dict(iter_price(state))
    assert len(x) == 3
    assert isinstance(x["Price"], float)
    assert isinstance(x["PriceDate"], datetime.date)
    assert isinstance(x["PriceTime"], datetime.time)


def test_state_iter_previous_price(state: dict[str, Any]) -> None:
    x = dict(iter_previous_price(state))
    assert len(x) == 3
    assert isinstance(x["PreviousPrice"], float)
    assert isinstance(x["PreviousPriceDate"], datetime.date)
    assert isinstance(x["PreviousPriceTime"], datetime.time)


def test_state_iter_index(state: dict[str, Any]) -> None:
    x = dict(iter_index(state))
    assert len(x) == 8
    assert isinstance(x["IssuedShares"], int)
    assert isinstance(x["IssuedSharesDate"], datetime.date)
    if x["BookValuePerShare"] is not None:
        assert isinstance(x["BookValuePerShare"], float)
        assert isinstance(x["BookValuePerShareDate"], datetime.date)
    if x["EarningsPerShare"] is not None:
        assert isinstance(x["EarningsPerShare"], float)
        assert isinstance(x["EarningsPerShareDate"], datetime.date)
    if x["DividendPerShare"] is not None:
        assert isinstance(x["DividendPerShare"], float)
        assert isinstance(x["DividendPerShareDate"], datetime.date)


def test_state_iter_press_release(state: dict[str, Any]) -> None:
    x = dict(iter_press_release(state))
    assert len(x) == 3
    if x["PressReleaseSummary"] is not None:
        assert isinstance(x["PressReleaseSummary"], str)
        assert isinstance(x["PressReleaseDate"], datetime.date)
        assert isinstance(x["PressReleaseTime"], datetime.time)


def test_state_iter_performance(state: dict[str, Any]) -> None:
    x = dict(iter_performance(state))
    assert len(x) == 6
    if x["PerformanceSummary"] is not None:
        assert isinstance(x["PerformanceSummary"], str)
        assert isinstance(x["PerformancePotential"], str)
        assert isinstance(x["PerformanceStability"], str)
        assert isinstance(x["PerformanceProfitability"], str)
        assert isinstance(x["PerformanceDate"], datetime.date)
        assert isinstance(x["PerformanceTime"], datetime.time)


def test_parse_quote(quote: str) -> None:
    df = parse_quote(quote)
    assert df.shape == (1, 23)


def test_parse_performance(performance: str) -> None:
    df = parse_performance(performance)
    assert df.width == 29 or df.equals(pl.DataFrame())
