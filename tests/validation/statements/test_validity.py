from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pytest
from polars import DataFrame
from polars import col as c

from tests.validation.conftest import pytestmark  # noqa: F401

if TYPE_CHECKING:
    from kabukit.domain.jquants.statements import Statements

# 指標が乖離している決算書を確認する必要あり


def test_equity_to_asset_ratio(data: DataFrame) -> None:
    x = data["EquityToAssetRatio"]
    y = data["Equity"] / data["TotalAssets"]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.93


def test_earnings_per_share(data: DataFrame) -> None:
    """EPS = 当期純利益 / 期中平均株式数"""
    x = data["EarningsPerShare"]
    y = data["Profit"] / data["AverageOutstandingShares"]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.98


@pytest.mark.parametrize("prefix", ["", "NextYear"])
@pytest.mark.parametrize("suffix", ["", "2ndQuarter"])
def test_forecast_earnings_per_share(data: DataFrame, prefix: str, suffix: str) -> None:
    """EPS_予想 = 純利益_予想 / 期中平均株式数"""
    x = data[f"{prefix}ForecastEarningsPerShare{suffix}"]
    y = data[f"{prefix}ForecastProfit{suffix}"] / data["AverageOutstandingShares"]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.94


def test_bookvalue_per_share(data: DataFrame) -> None:
    """BPS = 純資産 / 期中平均株式数"""
    x = data["BookValuePerShare"]
    y = data["Equity"] / data["AverageOutstandingShares"]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.9


def test_dividend_per_share(data: DataFrame) -> None:
    """DPS = 配当金 / 期中平均株式数"""
    x = data["ResultDividendPerShareAnnual"]
    y = data["ResultTotalDividendPaidAnnual"] / data["AverageOutstandingShares"]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.94


@pytest.mark.parametrize("prefix", ["Result", "Forecast", "NextYearForecast"])
def test_dividend_per_share_sum(data: DataFrame, prefix: str) -> None:
    x = data[f"{prefix}DividendPerShareAnnual"]
    y = (
        data[f"{prefix}DividendPerShare1stQuarter"]
        + data[f"{prefix}DividendPerShare2ndQuarter"]
        + data[f"{prefix}DividendPerShare3rdQuarter"]
        + data[f"{prefix}DividendPerShareFiscalYearEnd"]
    )
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.8


@pytest.mark.parametrize(
    ("d", "e"),
    [
        ("ResultDividendPerShareAnnual", "EarningsPerShare"),
        ("ResultTotalDividendPaidAnnual", "Profit"),
    ],
)
def test_payout_ratio(data: DataFrame, d: str, e: str) -> None:
    """配当性向 = 配当金 / 当期利益 = DPS / EPS"""
    x = data["ResultPayoutRatioAnnual"]
    y = data[d] / data[e]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.97


def test_earnings_per_share_consistency(data: DataFrame) -> None:
    """
    サマリーの利益額(Profit)は丸められている。
    決算短信の詳細数値を使うと、EPSを再現できることを示す。

    例: トレードワークス(3997) 2025年12月期 第2四半期決算短信
    <https://pdf.irpocket.com/C3997/bffO/ugVK/I9Yg.pdf>
    """
    x = data.filter(
        c.Code == "39970",
        c.DisclosedDate == date(2025, 8, 8),
    ).row(0, named=True)

    assert x["Profit"] == -69_000_000
    assert x["EarningsPerShare"] == -18.57

    actual_profit = -69_558_000  # 決算短信の詳細数値
    eps = actual_profit / x["AverageOutstandingShares"]
    assert round(eps, 2) == x["EarningsPerShare"]


@pytest.mark.parametrize(
    ("d", "n"),
    [
        (date(2025, 2, 5), 2699079277),
        (date(2025, 5, 8), 2746057686),
        (date(2025, 8, 7), 2761596216),
    ],
)
def test_shares_7203(statements: Statements, d: date, n: float) -> None:
    x = (
        statements.shares()
        .filter(c.Code == "72030", c.Date == d)
        .item(0, "TreasuryShares")
    )
    assert x == n


@pytest.mark.parametrize(
    ("d", "n"),
    [
        (date(2023, 2, 9), 28450023000000),
        (date(2025, 8, 7), 36993052000000),
    ],
)
def test_equity_7203(statements: Statements, d: date, n: float) -> None:
    x = statements.equity().filter(c.Code == "72030", c.Date == d).item(0, "Equity")
    assert x == n


@pytest.mark.parametrize(
    ("d", "n"),
    [
        (date(2024, 5, 8), 3570000000000),  # FY
        (date(2024, 8, 1), 3570000000000),  # 1Q
        (date(2024, 11, 6), 3570000000000),  # 2Q
        (date(2025, 2, 5), 4520000000000),  # 3Q
        (date(2025, 5, 8), 3100000000000),  # FY
    ],
)
def test_forecast_profit_7203(statements: Statements, d: date, n: float) -> None:
    x = (
        statements.forecast_profit()
        .filter(c.Code == "72030", c.Date == d)
        .item(0, "ForecastProfit")
    )
    assert x == n


@pytest.mark.parametrize(
    ("d", "n", "dps"),
    [
        (date(2025, 2, 17), 68917988, None),  # FY
        (date(2025, 5, 13), 68917988, 20),  # 1Q
        (date(2025, 8, 12), 68965517, 2),  # 2Q
    ],
)
def test_forecast_dividend_3997(
    statements: Statements,
    d: date,
    n: float,
    dps: float | None,
) -> None:
    x = (
        statements.forecast_dividend()
        .filter(c.Code == "39970", c.Date == d)
        .item(0, "ForecastDividend")
    )
    assert x == n

    x = statements.data.filter(
        c.Code == "39970",
        c.Date == d,
    ).item(0, "ForecastDividendPerShareAnnual")
    assert x == dps


def test_result_forecast_dividend_3997(statements: Statements) -> None:
    x = (
        statements.forecast_dividend()
        .filter(
            c.Code == "39970",
            c.Date == date(2024, 11, 15),
        )
        .item(0, "ForecastDividend")
    )
    assert x == 69_120_539

    x = statements.data.filter(
        c.Code == "39970",
        c.Date == date(2025, 2, 17),
    ).item(0, "ResultTotalDividendPaidAnnual")
    assert x == 68_000_000
