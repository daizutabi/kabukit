from __future__ import annotations

import datetime
from typing import Any


def test_quote_iter_price(quote: dict[str, Any]) -> None:
    from kabukit.sources.yahoo.parser import iter_price

    x = dict(iter_price(quote))
    assert len(x) == 3
    assert isinstance(x["Price"], float)
    assert isinstance(x["PriceDate"], datetime.date)
    assert isinstance(x["PriceTime"], datetime.time)


def test_quote_iter_previous_price(quote: dict[str, Any]) -> None:
    from kabukit.sources.yahoo.parser import iter_previous_price

    x = dict(iter_previous_price(quote))
    assert len(x) == 3
    assert isinstance(x["PreviousPrice"], float)
    assert isinstance(x["PreviousPriceDate"], datetime.date)
    assert isinstance(x["PreviousPriceTime"], datetime.time)


def test_quote_iter_press_release(quote: dict[str, Any]) -> None:
    from kabukit.sources.yahoo.parser import iter_press_release

    x = dict(iter_press_release(quote))
    assert len(x) == 3
    assert isinstance(x["PressReleaseSummary"], str)
    assert isinstance(x["PressReleaseDate"], datetime.date)
    assert isinstance(x["PressReleaseTime"], datetime.time)


def test_quote_iter_performance(quote: dict[str, Any]) -> None:
    from kabukit.sources.yahoo.parser import iter_performance

    x = dict(iter_performance(quote))
    assert len(x) == 6
    assert isinstance(x["PerformanceSummary"], str)
    assert isinstance(x["PerformancePotential"], str)
    assert isinstance(x["PerformanceStability"], str)
    assert isinstance(x["PerformanceProfitability"], str)
    assert isinstance(x["PerformanceDate"], datetime.date)
    assert isinstance(x["PerformanceTime"], datetime.time)
