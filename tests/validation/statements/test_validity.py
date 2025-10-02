from datetime import date

import pytest
from polars import DataFrame
from polars import col as c

from tests.validation.conftest import pytestmark  # noqa: F401

# 指標が乖離している決算書を確認する必要あり


def test_equity_to_asset_ratio(data: DataFrame) -> None:
    x = data["EquityToAssetRatio"]
    y = data["Equity"] / data["TotalAssets"]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.93


def test_earnings_per_share(data: DataFrame) -> None:
    """EPS = 当期純利益 / 発行済株式数"""
    x = data["EarningsPerShare"]
    y = data["Profit"] / data["AverageOutstandingShares"]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.98


def test_bookvalue_per_share(data: DataFrame) -> None:
    """BPS = 純資産 / 発行済株式数"""
    x = data["BookValuePerShare"]
    y = data["Equity"] / data["AverageOutstandingShares"]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.9


def test_dividend_per_share(data: DataFrame) -> None:
    """DPS = 配当金 / 発行済株式数"""
    x = data["ResultDividendPerShareAnnual"]
    y = data["ResultTotalDividendPaidAnnual"] / data["AverageOutstandingShares"]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.94


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


@pytest.mark.parametrize("prefix", ["", "NextYear"])
@pytest.mark.parametrize("suffix", ["", "2ndQuarter"])
def test_forecast_earnings_per_share(data: DataFrame, prefix: str, suffix: str) -> None:
    """EPS_予想 = 純利益_予想 / 発行済株式数"""
    x = data[f"{prefix}ForecastEarningsPerShare{suffix}"]
    y = data[f"{prefix}ForecastProfit{suffix}"] / data["AverageOutstandingShares"]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.94


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
