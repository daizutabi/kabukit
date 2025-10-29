from __future__ import annotations

import re
from typing import Any

import pytest
import pytest_asyncio

from kabukit.sources.yahoo.client import YahooClient


@pytest.fixture(scope="module", params=["7203"])
def code(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest_asyncio.fixture(scope="module")
async def quote(code: str):
    from kabukit.sources.yahoo.parser import get_preloaded_state

    async with YahooClient() as client:
        response = await client.get(f"{code}.T")
        yield get_preloaded_state(response.text)


def test_quote_press_release(quote: dict[str, Any]) -> None:
    x = quote["mainStocksPressReleaseSummary"]
    assert len(x) == 2
    assert "disclosedTime" in x
    assert "summary" in x


def test_quote_iter_press_release(quote: dict[str, Any]) -> None:
    from kabukit.sources.yahoo.parser import iter_press_release

    x = dict(iter_press_release(quote))
    assert len(x) == 3


def test_quote_performance(quote: dict[str, Any]) -> None:
    x = quote["stockPerformance"]["summaryInfo"]
    assert len(x) == 5
    assert "potential" in x
    assert "profitability" in x
    assert "stability" in x
    assert "summary" in x
    assert "updateTime" in x


def test_quote_detail(quote: dict[str, Any]) -> None:
    x = quote["mainStocksDetail"]["detail"]
    assert len(x) == 24
    assert "previousPrice" in x
    assert "previousPriceDate" in x


def test_quote_previous_price_date(quote: dict[str, Any]) -> None:
    x = quote["mainStocksDetail"]["detail"]["previousPriceDate"]
    assert re.match(r"^\d+[/:]\d+$", x)
