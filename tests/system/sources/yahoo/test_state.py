from __future__ import annotations

import re
from typing import Any


def test_quote_price(quote: dict[str, Any]) -> None:
    x = quote["mainStocksPriceBoard"]["priceBoard"]
    assert len(x) == 27
    assert "price" in x
    assert "priceDateTime" in x
    assert re.match(r"^\d+[/:]\d+$", x["priceDateTime"])


def test_quote_previous_price(quote: dict[str, Any]) -> None:
    x = quote["mainStocksDetail"]["detail"]
    assert len(x) == 24
    assert "previousPrice" in x
    assert "previousPriceDate" in x
    assert re.match(r"^\d+/\d+$", x["previousPriceDate"])


def test_quote_index(quote: dict[str, Any]) -> None:
    x = quote["mainStocksDetail"]["referenceIndex"]
    assert len(x) == 38
    assert "sharesIssued" in x
    assert "sharesIssuedDate" in x
    assert re.match(r"^\d+/\d+$", x["sharesIssuedDate"])
    for p in ["b", "e", "d"]:
        assert f"{p}ps" in x
        assert f"{p}psDate" in x
        assert re.match(r"^\d{4}/\d{2}$", x[f"{p}psDate"])


def test_quote_press_release(quote: dict[str, Any]) -> None:
    x = quote["mainStocksPressReleaseSummary"]
    assert len(x) == 2
    assert "disclosedTime" in x
    assert "summary" in x


def test_quote_performance(quote: dict[str, Any]) -> None:
    x = quote["stockPerformance"]["summaryInfo"]
    assert len(x) == 5
    assert "potential" in x
    assert "profitability" in x
    assert "stability" in x
    assert "summary" in x
    assert "updateTime" in x
