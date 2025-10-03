from datetime import date

import pytest
import pytest_asyncio
from polars import DataFrame
from polars import col as c

from kabukit.core.prices import Prices
from kabukit.core.statements import Statements
from kabukit.jquants.concurrent import fetch
from tests.validation.conftest import pytestmark  # noqa: F401


@pytest_asyncio.fixture(scope="module")
async def prices(statements: Statements) -> Prices:
    codes = ["3350", "6200", "3399", "7187", "6542", "3816", "4923", "3997"]
    data = await fetch("prices", codes)
    return Prices(data).with_adjusted_shares(statements)


@pytest.fixture(scope="module")
def data(prices: Prices) -> DataFrame:
    data = prices.data

    return (
        data.with_columns(
            MarketCap=c.RawClose * c.AdjustedIssuedShares,
        )
        .with_columns(
            PrevMarketCap=c.MarketCap.shift(1).over("Code"),
            PrevClose=c.Close.shift(1).over("Code"),
        )
        .filter(c.AdjustmentFactor != 1)
        .with_columns(
            Ratio=(c.MarketCap - c.PrevMarketCap).abs() / c.PrevMarketCap,
            CloseRatio=(c.Close - c.PrevClose).abs() / c.PrevClose,
        )
        .with_columns(
            RatioRatio=c.Ratio / c.CloseRatio,
        )
    )


def test_adjusted_shares_ratio_min(data: DataFrame) -> None:
    x = data["Ratio"].mean()
    assert isinstance(x, float)
    assert x < 0.05


def test_adjusted_shares_ratio_max(data: DataFrame) -> None:
    x = data["Ratio"].max()
    assert isinstance(x, float)
    assert x < 0.25


def test_adjusted_shares_ratio_ratio_min(data: DataFrame) -> None:
    x = data["RatioRatio"].min()
    assert isinstance(x, float)
    assert x > 0.995


def test_adjusted_shares_ratio_ratio_max(data: DataFrame) -> None:
    x = data["RatioRatio"].max()
    assert isinstance(x, float)
    assert x < 1.05


def test_adjusted_shares_3997(prices: Prices) -> None:
    df = prices.filter(c.Code == "39970").data
    a = df.filter(c.Date == date(2025, 9, 26)).row(0, named=True)
    assert a["AdjustmentFactor"] == 1
    assert a["RawClose"] == 3610
    assert a["AdjustedIssuedShares"] == 3901800

    b = df.filter(c.Date == date(2025, 9, 29)).row(0, named=True)
    assert b["AdjustmentFactor"] == 0.1
    assert b["RawClose"] == 353
    assert b["AdjustedIssuedShares"] == 39018000

    x = a["RawClose"] * a["AdjustedIssuedShares"]
    y = b["RawClose"] * b["AdjustedIssuedShares"]
    assert x / y == 361 / 353


def test_adjusted_shares_3350(prices: Prices) -> None:
    df = prices.filter(c.Code == "33500").data
    a = df.filter(c.Date == date(2024, 7, 29)).row(0, named=True)
    assert a["AdjustmentFactor"] == 1
    assert a["RawClose"] == 201
    assert a["AdjustedIssuedShares"] == 114692187

    b = df.filter(c.Date == date(2024, 7, 30)).row(0, named=True)
    assert b["AdjustmentFactor"] == 10
    assert b["RawClose"] == 1510
    assert b["AdjustedIssuedShares"] == 11469219

    x = a["RawClose"] * a["AdjustedIssuedShares"]
    y = b["RawClose"] * b["AdjustedIssuedShares"]
    assert round(x / y, 7) == round(201 / 151, 7)


def test_adjusted_shares_6200(prices: Prices) -> None:
    df = prices.filter(c.Code == "62000").data
    a = df.filter(c.Date == date(2022, 12, 28)).row(0, named=True)
    assert a["AdjustmentFactor"] == 1
    assert a["RawClose"] == 3095
    assert a["AdjustedIssuedShares"] == 42621500

    b = df.filter(c.Date == date(2022, 12, 29)).row(0, named=True)
    assert b["AdjustmentFactor"] == 0.5
    assert b["RawClose"] == 1534
    assert b["AdjustedIssuedShares"] == 85243000

    x = a["RawClose"] * a["AdjustedIssuedShares"]
    y = b["RawClose"] * b["AdjustedIssuedShares"]
    assert x / y == 3095 / 2 / 1534
