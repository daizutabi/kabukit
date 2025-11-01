from __future__ import annotations

import re
from typing import Any


def test_state_price(state: dict[str, Any]) -> None:
    x = state["mainStocksPriceBoard"]["priceBoard"]
    assert len(x) == 27
    assert "price" in x
    assert "priceDateTime" in x
    assert re.match(r"^\d+[/:]\d+$", x["priceDateTime"])


def test_state_previous_price(state: dict[str, Any]) -> None:
    x = state["mainStocksDetail"]["detail"]
    assert len(x) == 24
    assert "previousPrice" in x
    assert "previousPriceDate" in x
    assert re.match(r"^\d+/\d+$", x["previousPriceDate"])


def test_state_index(state: dict[str, Any]) -> None:
    x = state["mainStocksDetail"]["referenceIndex"]
    assert len(x) == 38
    assert "sharesIssued" in x
    assert "sharesIssuedDate" in x
    assert re.match(r"^\d+/\d+$", x["sharesIssuedDate"])
    for p in ["b", "e", "d"]:
        assert f"{p}ps" in x
        assert f"{p}psDate" in x
        assert re.match(r"^\d{4}/\d{2}$", x[f"{p}psDate"])


def test_state_press_release(state: dict[str, Any]) -> None:
    x = state["mainStocksPressReleaseSummary"]
    assert len(x) == 2
    assert "disclosedTime" in x
    assert "summary" in x


def test_state_performance(state: dict[str, Any]) -> None:
    x = state["stockPerformance"]["summaryInfo"]
    assert len(x) == 5
    assert "potential" in x
    assert "profitability" in x
    assert "stability" in x
    assert "summary" in x
    assert "updateTime" in x


def test_store_preformance(store: dict[str, Any]) -> None:
    x = store["performance"]["performance"]

    assert isinstance(x, list)

    for record in x:  # pyright: ignore[reportUnknownVariableType]
        assert isinstance(record, dict)
        assert len(record) == 29  # pyright: ignore[reportUnknownArgumentType]


def test_store_forcast(store: dict[str, Any]) -> None:
    x = store["performance"]["forecast"]

    assert isinstance(x, dict)
    assert len(x) == 7  # pyright: ignore[reportUnknownArgumentType]
