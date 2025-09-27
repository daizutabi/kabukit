import polars as pl
import pytest
from polars import DataFrame, Series
from polars import col as c

from kabukit.core.statements import Statements

try:
    stmts = Statements.read()
except FileNotFoundError:
    stmts = None

pytestmark = [
    pytest.mark.validation,
    pytest.mark.skipif(
        stmts is None,
        reason="No data found. Run `kabu get statements` first.",
    ),
]


@pytest.fixture(scope="module")
def data() -> DataFrame:
    assert stmts is not None
    return stmts.data


def test_width(data: DataFrame) -> None:
    assert data.width == 104


def test_height(data: DataFrame) -> None:
    assert data.height > 160_000


@pytest.mark.parametrize(
    "column",
    [
        "Date",
        "Code",
        "DisclosureNumber",
        "TypeOfDocument",
        "CurrentPeriodStartDate",
        "CurrentPeriodEndDate",
        "CurrentFiscalYearStartDate",
        "CurrentFiscalYearEndDate",
    ],
)
def test_is_not_null_all(data: DataFrame, column: str) -> None:
    assert data[column].is_not_null().all()


@pytest.mark.parametrize("column", ["Time"])
def test_is_not_null_any(data: DataFrame, column: str) -> None:
    assert data[column].is_not_null().any()


@pytest.fixture(scope="module")
def tod(data: DataFrame) -> Series:
    return data["TypeOfDocument"].unique()


def test_type_of_document_financial_period(tod: Series) -> None:
    x = (
        tod.filter(tod.str.contains("Financial"))
        .str.split("Financial")
        .list.first()
        .unique()
    )
    assert sorted(x) == ["1Q", "2Q", "3Q", "FY", "OtherPeriod"]


def test_type_of_document_financial_consolidated(tod: Series) -> None:
    x = tod.filter(tod.str.contains("Financial")).str.split("_").list[1].unique()
    assert sorted(x) == ["Consolidated", "NonConsolidated"]


def test_type_of_document_financial_type(tod: Series) -> None:
    x = tod.filter(tod.str.contains("Financial")).str.split("_").list.last().unique()
    assert sorted(x) == ["Foreign", "IFRS", "JP", "US"]


def test_type_of_document_other(tod: Series) -> None:
    x = tod.filter(tod.str.contains("Financial").not_()).unique()
    assert sorted(x) == ["DividendForecastRevision", "EarnForecastRevision"]


@pytest.fixture(scope="module")
def pct(data: DataFrame) -> DataFrame:
    return (
        data.filter(c.TypeOfDocument.str.starts_with("Other").not_())
        .group_by(c.TypeOfDocument.str.split("_").list.first())
        .agg(pl.len(), pl.all().is_not_null().sum())
        .with_columns(
            pl.exclude("TypeOfDocument", "len") / pl.col("len") * 100,
        )
    ).sort("TypeOfDocument")


@pytest.mark.parametrize(
    "column",
    ["NextFiscalYearStartDate", "NextFiscalYearEndDate"],
)
def test_next_fiscal_year_start_end(pct: DataFrame, column: str) -> None:
    cond = c.TypeOfDocument.str.starts_with("FY")

    # FY決算のうち、次期の期首・期末が存在する割合は90%以上
    assert pct.filter(cond)[column].gt(90).all()

    # FY決算以外では、次期の期首・期末は欠損
    assert pct.filter(cond.not_())[column].eq(0).all()


@pytest.mark.parametrize(
    "column",
    ["NetSales", "OperatingProfit", "Profit", "EarningsPerShare"],
)
def test_pl_columns(pct: DataFrame, column: str) -> None:
    cond = c.TypeOfDocument.str.contains("FinancialStatements")

    # 決算では、P/L項目が存在する割合は85%以上
    assert pct.filter(cond)[column].gt(85).all()

    # 決算以外では、P/L項目は欠損
    assert pct.filter(cond.not_())[column].eq(0).all()
