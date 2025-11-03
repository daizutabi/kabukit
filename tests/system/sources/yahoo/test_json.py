from __future__ import annotations

import re
from typing import Any

import pytest

pytestmark = pytest.mark.system


def test_state_price(state: dict[str, Any]) -> None:
    x = state["mainStocksPriceBoard"]["priceBoard"]
    assert len(x) in [26, 27]
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
        assert re.match(r"^[\d-]{4}/[\d-]{2}$", x[f"{p}psDate"])


def test_state_press_release(state: dict[str, Any]) -> None:
    x = state["mainStocksPressReleaseSummary"]
    if not x:
        pass
    elif len(x) == 1:
        assert "disclosedTime" in x
    else:
        assert len(x) == 2
        assert "disclosedTime" in x
        assert "summary" in x


def test_state_performance(state: dict[str, Any]) -> None:
    x = state["stockPerformance"]
    if "summaryInfo" in x:
        x = x["summaryInfo"]
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
    assert len(x) in [0, 5, 7, 9]  # pyright: ignore[reportUnknownArgumentType]
