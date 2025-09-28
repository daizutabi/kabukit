import pytest
from polars import DataFrame

from .conftest import COMMON_COLUMNS, pytestmark  # noqa: F401


def test_earnings_per_share(data: DataFrame) -> None:
    """EPS = 当期純利益 / 発行済株式数"""
    x = data["EarningsPerShare"]
    y = data["Profit"] / data["AverageNumberOfShares"]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.98


def test_bookvalue_per_share(data: DataFrame) -> None:
    """BPS = 純資産 / 発行済株式数"""
    x = data["BookValuePerShare"]
    y = data["Equity"] / data["AverageNumberOfShares"]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.9


def test_dividend_per_share(data: DataFrame) -> None:
    """DPS = 配当金 / 発行済株式数"""
    x = data["ResultDividendPerShareAnnual"]
    y = data["ResultTotalDividendPaidAnnual"] / data["AverageNumberOfShares"]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.94


def test_payout_ratio(data: DataFrame) -> None:
    """配当性向 = DPS / EPS"""
    x = data["ResultPayoutRatioAnnual"]
    y = data["ResultDividendPerShareAnnual"] / data["EarningsPerShare"]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.97


@pytest.mark.parametrize("prefix", ["", "NextYear"])
@pytest.mark.parametrize("suffix", ["", "2ndQuarter"])
def test_forecast_earnings_per_share(data: DataFrame, prefix: str, suffix: str) -> None:
    """EPS_予想 = 純利益_予想 / 発行済株式数"""
    x = data[f"{prefix}ForecastEarningsPerShare{suffix}"]
    y = data[f"{prefix}ForecastProfit{suffix}"] / data["AverageNumberOfShares"]
    r = x / y
    m = ((r > 0.9) & (r < 1.1)).mean()
    assert isinstance(m, float)
    assert m > 0.94
