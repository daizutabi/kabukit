from __future__ import annotations

import polars as pl
import pytest
from polars import col as c

from tests.validation.conftest import pytestmark  # noqa: F401


def test_fin_profit_loss(fin: pl.DataFrame, pl_col: str) -> None:
    """決算の損益計算書の各項目は、ほぼ100%埋まっている"""
    x = fin[pl_col].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.938 < x <= 1.0  # 割合 1 に近い


@pytest.mark.parametrize("kind", ["US", "IFRS"])
def test_fin_ordinary_profit(fin: pl.DataFrame, kind: str) -> None:
    """US・IFRS基準の決算では、OrdinaryProfitはほとんど存在しない"""
    df = fin.filter(c.TypeOfDocument.str.contains(kind))
    x = df["OrdinaryProfit"].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.0 < x <= 0.025  # ごく一部のみ


def test_fin_diluted_earnings_per_share(fin: pl.DataFrame) -> None:
    """DilutedEarningsPerShareは、30%程度が埋まっている"""
    x = fin["DilutedEarningsPerShare"].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.30 < x <= 0.32  # 30% くらい


def test_fin_balance_sheet(fin: pl.DataFrame, bs_col: str) -> None:
    """決算の貸借対照表の各項目は、ほぼ100%埋まっている。ただし、BookValuePerShareは約45%"""
    x = fin[bs_col].is_not_null().mean()
    assert isinstance(x, float)

    if bs_col != "BookValuePerShare":
        assert 0.99 < x <= 1.0  # 割合 1 に近い
    else:
        assert 0.45 < x <= 0.47


@pytest.mark.parametrize(
    ("period", "low", "high"),
    [
        ("1Q", 0.10, 0.12),
        ("2Q", 0.75, 0.77),
        ("3Q", 0.10, 0.12),
        ("FY", 0.99, 1.00),
        ("OtherPeriod", 0.75, 0.85),
    ],
)
def test_fin_cash_flow(
    fin: pl.DataFrame,
    cf_col: str,
    period: str,
    low: float,
    high: float,
) -> None:
    """決算のキャッシュフロー計算書の各項目がどの程度埋まっているか"""
    df = fin.filter(c.TypeOfDocument.str.starts_with(period))
    x = df[cf_col].is_not_null().mean()
    assert isinstance(x, float)
    assert low < x < high


@pytest.mark.parametrize(
    ("period", "name", "low", "high"),
    [
        ("1Q", "1stQuarter", 0.007, 0.009),
        ("1Q", "2ndQuarter", 0, 0),
        ("1Q", "3rdQuarter", 0, 0),
        ("1Q", "FiscalYearEnd", 0, 0),
        ("2Q", "1stQuarter", 0.007, 0.009),
        ("2Q", "2ndQuarter", 0.92, 0.96),
        ("2Q", "3rdQuarter", 0, 0),
        ("2Q", "FiscalYearEnd", 0, 0),
        ("3Q", "1stQuarter", 0.007, 0.009),
        ("3Q", "2ndQuarter", 0.92, 0.96),
        ("3Q", "3rdQuarter", 0.007, 0.009),
        ("3Q", "FiscalYearEnd", 0, 0.0002),  # 誤登録の可能性あり
        ("FY", "1stQuarter", 0.007, 0.009),
        ("FY", "2ndQuarter", 0.92, 0.96),
        ("FY", "3rdQuarter", 0.007, 0.009),
        ("FY", "FiscalYearEnd", 0.98, 1),
    ],
)
def test_fin_result_dividend(
    fin: pl.DataFrame,
    period: str,
    name: str,
    low: float,
    high: float,
) -> None:
    """決算の配当実績がどの程度埋まっているか"""
    df = fin.filter(c.TypeOfDocument.str.starts_with(period))
    x = df[f"ResultDividendPerShare{name}"].is_not_null().mean()
    assert isinstance(x, float)
    assert low <= x <= high


@pytest.mark.parametrize(
    ("column", "low", "high"),
    [
        ("ResultDividendPerShareAnnual", 0.96, 0.98),
        ("ResultTotalDividendPaidAnnual", 0.84, 0.86),
        ("ResultPayoutRatioAnnual", 0.77, 0.79),
    ],
)
def test_fin_result_dividend_annual(
    fin: pl.DataFrame,
    column: str,
    low: float,
    high: float,
) -> None:
    """通期決算では、年間配当実績がほぼ埋まっている"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("FY"))
    x = df[column].is_not_null().mean()
    assert isinstance(x, float)
    assert low <= x <= high


def test_fin_result_dividend_other_period(fin: pl.DataFrame) -> None:
    """OtherPerid決算では、配当実績なし"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("OtherPeriod")).select(
        pl.col("^ResultDividend.*$"),
    )
    assert all(df[c].is_null().all() for c in df.columns)


@pytest.mark.parametrize(
    ("period", "name", "low", "high"),
    [
        ("1Q", "1stQuarter", 0, 3e-5),  # 誤登録の可能性あり
        ("1Q", "2ndQuarter", 0.85, 0.87),
        ("1Q", "3rdQuarter", 0.006, 0.008),
        ("1Q", "FiscalYearEnd", 0.89, 0.93),
        ("2Q", "1stQuarter", 0, 0),
        ("2Q", "2ndQuarter", 0, 4e-4),  # 誤登録の可能性あり
        ("2Q", "3rdQuarter", 0.006, 0.008),
        ("2Q", "FiscalYearEnd", 0.89, 0.93),
        ("3Q", "1stQuarter", 0, 0),
        ("3Q", "2ndQuarter", 0, 6e-5),  # 誤登録の可能性あり
        ("3Q", "3rdQuarter", 0, 0),
        ("3Q", "FiscalYearEnd", 0.90, 0.94),
        ("FY", "1stQuarter", 0, 0),
        ("FY", "2ndQuarter", 0, 0),
        ("FY", "3rdQuarter", 0, 0),
        ("FY", "FiscalYearEnd", 0, 3e-5),  # 誤登録の可能性あり
    ],
)
def test_fin_forecast_dividend(
    fin: pl.DataFrame,
    period: str,
    name: str,
    low: float,
    high: float,
) -> None:
    """決算の配当予想がどの程度埋まっているか"""
    df = fin.filter(c.TypeOfDocument.str.starts_with(period))
    x = df[f"ForecastDividendPerShare{name}"].is_not_null().mean()
    assert isinstance(x, float)
    assert low <= x <= high


@pytest.mark.parametrize(
    ("column", "low", "high"),
    [
        ("ForecastDividendPerShareAnnual", 0.88, 0.92),
    ],
)
def test_fin_forecast_dividend_annual(
    fin: pl.DataFrame,
    column: str,
    low: float,
    high: float,
) -> None:
    """通期決算以外において、年間配当予想がある程度埋まっている"""
    df = fin.filter(~c.TypeOfDocument.str.starts_with("FY"))
    x = df[column].is_not_null().mean()
    assert isinstance(x, float)
    assert low <= x <= high


@pytest.mark.parametrize(
    "column",
    [
        "ForecastTotalDividendPaidAnnual",
        "ForecastPayoutRatioAnnual",
    ],
)
def test_forecast_dividend_annual_null(fin: pl.DataFrame, column: str) -> None:
    """通期決算以外において、年間配当予想の総額と配当性向はnull"""
    df = fin.filter(~c.TypeOfDocument.str.starts_with("FY"))
    assert df[column].is_null().all()


@pytest.mark.parametrize(
    ("name", "low", "high"),
    [
        ("1stQuarter", 0.004, 0.007),
        ("2ndQuarter", 0.82, 0.85),
        ("3rdQuarter", 0.004, 0.007),
        ("FiscalYearEnd", 0.85, 0.90),
    ],
)
def test_fin_next_year_forecast_dividend(
    fin: pl.DataFrame,
    name: str,
    low: float,
    high: float,
) -> None:
    """FY決算では、次期の配当予想がある程度埋まっている"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("FY"))
    x = df[f"NextYearForecastDividendPerShare{name}"].is_not_null().mean()
    assert isinstance(x, float)
    assert low <= x <= high


@pytest.mark.parametrize(
    ("column", "low", "high"),
    [
        ("NextYearForecastDividendPerShareAnnual", 0.85, 0.88),
        ("NextYearForecastPayoutRatioAnnual", 0.66, 0.70),
    ],
)
def test_fin_next_year_forecast_dividend_annual(
    fin: pl.DataFrame,
    column: str,
    low: float,
    high: float,
) -> None:
    """FY決算では、次期の年間配当予想がある程度埋まっている"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("FY"))
    x = df[column].is_not_null().mean()
    assert isinstance(x, float)
    assert low <= x <= high


def test_fin_next_year_forecast_dividend_annual_column(fin: pl.DataFrame) -> None:
    """NextYearForecastTotalDividendPaidAnnualが欠落。"""
    assert "ForecastDividendPerShareAnnual" in fin.columns
    assert "ForecastPayoutRatioAnnual" in fin.columns
    assert "ForecastTotalDividendPaidAnnual" in fin.columns

    assert "NextYearForecastDividendPerShareAnnual" in fin.columns
    assert "NextYearForecastPayoutRatioAnnual" in fin.columns
    assert "NextYearForecastTotalDividendPaidAnnual" not in fin.columns


def test_fin_next_year_forecast(fin: pl.DataFrame) -> None:
    """FY決算以外では、次期の予想は存在しない"""
    df = fin.filter(~c.TypeOfDocument.str.starts_with("FY")).select(
        pl.col("^NextYear.*$"),
    )
    assert all(df[c].is_null().all() for c in df.columns)


def test_fin_forecast(fin: pl.DataFrame) -> None:
    """FY決算では、当期の予想は存在しない。ただし、誤登録の可能性あり"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("FY")).select(
        pl.col("^Forecast.*$"),
    )
    x = [df[c].is_null().mean() for c in df.columns]
    x = [x for x in x if isinstance(x, float)]
    assert len(x) == 27
    assert all(0.999 < v <= 1.0 for v in x)


def test_fin_forecast_other(fin: pl.DataFrame) -> None:
    """OtherPeriod決算では、当期の予想は存在しない"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("OtherPeriod")).select(
        pl.col("^Forecast.*$"),
    )
    assert all(df[c].is_null().all() for c in df.columns)


@pytest.mark.parametrize(
    ("period", "low", "high"),
    [
        ("1Q", 0.53, 0.57),
        ("2Q", 0.0, 2e-4),  # 誤登録の可能性あり
        ("3Q", 0.0, 4e-5),  # 誤登録の可能性あり
        ("FY", 0.0, 0.0),
    ],
)
def test_fin_forecast_profit_loss_2nd_quarter(
    fin: pl.DataFrame,
    pl_col: str,
    period: str,
    low: float,
    high: float,
) -> None:
    """決算の2Q業績予想の損益計算書の各項目がどの程度埋まっているか"""
    df = fin.filter(c.TypeOfDocument.str.starts_with(period))
    x = df[f"Forecast{pl_col}2ndQuarter"].is_not_null().mean()
    assert isinstance(x, float)
    assert low <= x <= high


def test_fin_next_year_forecast_profit_loss_2nd_quarter(
    fin: pl.DataFrame,
    pl_col: str,
) -> None:
    """FY決算では、次期の2Q業績予想の損益計算書の各項目が50%程度埋まっている"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("FY"))
    x = df[f"NextYearForecast{pl_col}2ndQuarter"].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.50 <= x <= 0.55


def test_fin_forecast_profit_loss(fin: pl.DataFrame, pl_col: str) -> None:
    """FY決算以外では、期末業績予想の損益計算書の各項目が90%程度埋まっている"""
    df = fin.filter(
        ~c.TypeOfDocument.str.starts_with("FY"),
        ~c.TypeOfDocument.str.starts_with("OtherPeriod"),
    )
    x = df[f"Forecast{pl_col}"].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.86 <= x <= 0.95


def test_fin_next_year_forecast_profit_loss(fin: pl.DataFrame, pl_col: str) -> None:
    """FY決算では、次期の期末業績予想の損益計算書の各項目が85%程度埋まっている"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("FY"))
    x = df[f"NextYearForecast{pl_col}"].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.80 <= x <= 0.90


@pytest.fixture(
    scope="module",
    params=["IssuedShares", "TreasuryShares", "AverageOutstandingShares"],
)
def col_shares(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.mark.parametrize("period", ["1Q", "2Q", "3Q", "FY"])
def test_fin_shares(fin: pl.DataFrame, period: str, col_shares: str) -> None:
    """決算の株式数は、ほぼ100%埋まっている"""
    df = fin.filter(c.TypeOfDocument.str.starts_with(period))
    x = df[col_shares].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.94 < x <= 1.0  # 割合 1 に近い


def test_fin_shares_other(fin: pl.DataFrame, col_shares: str) -> None:
    """OtherPeriod決算では、株式数は存在しない"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("OtherPeriod"))
    assert df[col_shares].is_null().all()


def test_earn_revision_column_name_starts_with_forecast(
    earn_revision: pl.DataFrame,
) -> None:
    """業績修正のカラム名が "Forecast" で始まる"""
    assert all(c.startswith("Forecast") for c in earn_revision.columns)


def test_earn_revision_profit_loss_fiscal_year_end(
    earn_revision: pl.DataFrame,
    pl_col: str,
) -> None:
    """業績修正の期末業績予想の損益項目の各項目がどの程度埋まっているか"""
    x = earn_revision[f"Forecast{pl_col}"].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.65 < x < 0.70  # 割合 3/4 くらい


def test_earn_revision_profit_loss_2nd_quarter(
    earn_revision: pl.DataFrame,
    pl_col: str,
) -> None:
    """業績修正の2Q業績予想の損益項目の各項目がどの程度埋まっているか"""
    x = earn_revision[f"Forecast{pl_col}2ndQuarter"].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.258 < x < 0.29  # 割合 1/4 くらい


@pytest.mark.parametrize(
    ("name", "low", "high"),
    [
        ("1stQuarter", 0.003, 0.004),
        ("2ndQuarter", 0.05, 0.06),
        ("3rdQuarter", 0.003, 0.004),
        ("FiscalYearEnd", 0.15, 0.17),
        ("Annual", 0.15, 0.17),
    ],
)
def test_earn_revision_dividend(
    earn_revision: pl.DataFrame,
    name: str,
    high: float,
    low: float,
) -> None:
    """業績修正の配当予想の各項目がどの程度埋まっているか"""
    x = earn_revision[f"ForecastDividendPerShare{name}"].is_not_null().mean()
    assert isinstance(x, float)
    assert low < x < high


@pytest.mark.parametrize(
    ("name", "low", "high"),
    [
        ("1stQuarter", 0.028, 0.032),
        ("2ndQuarter", 0.3, 0.32),
        ("3rdQuarter", 0.028, 0.032),
        ("FiscalYearEnd", 0.92, 0.98),
        ("Annual", 0.85, 0.90),
    ],
)
def test_dividend_revision_dividend(
    dividend_revision: pl.DataFrame,
    name: str,
    high: float,
    low: float,
) -> None:
    """配当修正の配当予想の各項目がどの程度埋まっているか"""
    x = dividend_revision[f"ForecastDividendPerShare{name}"].is_not_null().mean()
    assert isinstance(x, float)
    assert low < x < high
