from __future__ import annotations

import polars as pl
import pytest
from polars import col as c

from tests.validation.conftest import pytestmark  # noqa: F401

from .conftest import COMMON_COLUMNS


def test_width(data: pl.DataFrame) -> None:
    assert data.width == 105


def test_height(data: pl.DataFrame) -> None:
    assert data.height > 160_000


@pytest.mark.parametrize(
    "column",
    [c for c in COMMON_COLUMNS if c not in ["DisclosedTime"]],
)
def test_is_not_null_all(data: pl.DataFrame, column: str) -> None:
    """共通カラムのうち、Time以外は全て非欠損"""
    assert data[column].is_not_null().all()


@pytest.mark.parametrize("column", ["DisclosedTime"])
def test_is_not_null_any(data: pl.DataFrame, column: str) -> None:
    """Timeカラムは一部欠損"""
    assert data[column].is_null().any()


@pytest.fixture(scope="module")
def tod(data: pl.DataFrame) -> pl.Series:
    """TypeOfDocumentのユニークな値一覧"""
    return data["TypeOfDocument"].unique()


@pytest.fixture(scope="module")
def tod_fin(tod: pl.Series) -> pl.Series:
    """TypeOfDocumentのうち、決算関連のものだけ抽出"""
    return tod.filter(tod.str.contains("Financial"))


def test_type_of_document_financial_period(tod_fin: pl.Series) -> None:
    """決算の期間は、(1Q, 2Q, 3Q, FY, OtherPeriod)"""
    x = tod_fin.str.split("Financial").list.first().unique()
    assert sorted(x) == ["1Q", "2Q", "3Q", "FY", "OtherPeriod"]


def test_type_of_document_financial_consolidated(tod_fin: pl.Series) -> None:
    """決算の連結・非連結の区分は、(Consolidated, NonConsolidated)"""
    x = tod_fin.str.split("_").list[1].unique()
    assert sorted(x) == ["Consolidated", "NonConsolidated"]


def test_type_of_document_financial_type(tod_fin: pl.Series) -> None:
    """決算の会計基準は、(JP, US, IFRS, Foreign)"""
    x = tod_fin.str.split("_").list.last().unique()
    assert sorted(x) == ["Foreign", "IFRS", "JP", "US"]


def test_type_of_document_dividend_and_earn_forecast(tod: pl.Series) -> None:
    """決算以外のTypeOfDocumentは、(DividendForecastRevision, EarnForecastRevision)"""
    x = tod.filter(tod.str.contains("Financial").not_()).unique()
    assert sorted(x) == ["DividendForecastRevision", "EarnForecastRevision"]


def test_type_of_document_other_period(tod_fin: pl.Series) -> None:
    """OtherPeriodFinancialStatementsの種類を確認。今後増える可能性がある"""
    x = (
        tod_fin.filter(tod_fin.str.starts_with("Other"))
        .str.split("_")
        .list.slice(-2)
        .list.join("_")
        .unique()
    )
    assert sorted(x) == ["Consolidated_IFRS", "Consolidated_JP", "NonConsolidated_JP"]


@pytest.mark.parametrize(
    ("name", "length"),
    [
        ("OtherPeriodFinancialStatements_Consolidated_JP", 21),
        ("OtherPeriodFinancialStatements_Consolidated_IFRS", 1),
        ("OtherPeriodFinancialStatements_NonConsolidated_JP", 2),
    ],
)
def test_type_of_document_other_period_length(
    data: pl.DataFrame,
    name: str,
    length: int,
) -> None:
    """OtherPeriodFinancialStatementsの種類ごとの件数を確認。今後増える可能性がある。"""
    assert data.filter(c.TypeOfDocument == name).height == length


@pytest.mark.parametrize(
    "column",
    ["NextFiscalYearStartDate", "NextFiscalYearEndDate"],
)
def test_next_fiscal_year_start_end(data: pl.DataFrame, column: str) -> None:
    """次期の期首・期末の欠損状況を確認

    - FY決算のうち、次期の期首・期末が存在する割合は99%以上だが、100%ではない。
    - FY決算以外では、次期の期首・期末は欠損
    """
    cond = c.TypeOfDocument.str.starts_with("FY")

    # FY決算
    x = data.filter(cond)[column].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.99 <= x < 1.0

    # FY決算以外
    assert data.filter(~cond)[column].is_null().all()


@pytest.mark.parametrize("period", ["1Q", "2Q", "3Q", "FY"])
def test_fin_current_period_equality(fin: pl.DataFrame, period: str) -> None:
    """決算の期間の分布を確認"""
    df = fin.filter(c.TypeOfDocument.str.starts_with(period))
    x = df["TypeOfCurrentPeriod"].eq(period).mean()
    assert isinstance(x, float)
    if period == "FY":
        assert x == 1
    else:
        assert 0.9995 < x < 1  # 一致しないものがごく一部ある


@pytest.mark.parametrize(
    ("period", "days"),
    [("1Q", 90), ("2Q", 180), ("3Q", 270), ("FY", 365)],
)
def test_fin_current_period_days(fin: pl.DataFrame, period: str, days: int) -> None:
    """決算の期間の日数を確認。例外があるが、ほぼ標準的な日数になっている"""
    df = (
        fin.filter(c.TypeOfDocument.str.starts_with(period))
        .select(
            x=(c.CurrentPeriodEndDate - c.CurrentPeriodStartDate).dt.total_days() + 1,
        )
        .select((c.x > days - 3) & (c.x < days + 8))
    )
    x = df["x"].mean()
    assert isinstance(x, float)
    assert 0.994 < x <= 1


def test_per_share(data: pl.DataFrame) -> None:
    df = data.select(pl.col("^.*PerShare.*$"))
    assert df.width == 28


@pytest.mark.parametrize(
    "name",
    ["DividendPerShare", "TotalDividendPaid", "PayoutRatio"],
)
def test_result_annual(data: pl.DataFrame, name: str) -> None:
    df = data.select(pl.col("^Result.*Annual$"))
    assert df.width == 3
    assert f"Result{name}Annual" in df.columns


@pytest.mark.parametrize(
    "name",
    ["DividendPerShare", "TotalDividendPaid", "PayoutRatio"],
)
def test_forecast_annual(data: pl.DataFrame, name: str) -> None:
    df = data.select(pl.col("^Forecast.*Annual$"))
    assert df.width == 3
    assert f"Forecast{name}Annual" in df.columns


@pytest.mark.parametrize(
    "name",
    ["DividendPerShare", "PayoutRatio"],
)
def test_next_year_forecast_annual(data: pl.DataFrame, name: str) -> None:
    """NextYearForecastは、TotalDividendPaidが存在しない"""
    df = data.select(pl.col("^NextYearForecast.*Annual$"))
    assert df.width == 2
    assert f"NextYearForecast{name}Annual" in df.columns


def test_earn_revision_width(earn_revision: pl.DataFrame) -> None:
    assert earn_revision.width == 25


def test_dividend_revision_width(dividend_revision: pl.DataFrame) -> None:
    assert dividend_revision.width == 5
