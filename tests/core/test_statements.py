import polars as pl
import pytest
from polars import DataFrame
from polars import col as c


@pytest.fixture(scope="module")
def df() -> DataFrame:
    from kabukit.core.statements import Statements

    return Statements.read().data


def test_width(df: DataFrame) -> None:
    assert df.width == 75


def test_heigth(df: DataFrame) -> None:
    assert df.height > 150_000


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
def test_is_not_null_all(df: DataFrame, column: str) -> None:
    assert df[column].is_not_null().all()


@pytest.mark.parametrize("column", ["Time"])
def test_is_null_any(df: DataFrame, column: str) -> None:
    assert df[column].is_not_null().any()


@pytest.fixture(scope="module")
def pct(df: DataFrame) -> DataFrame:
    return (
        df.filter(c.TypeOfDocument.str.starts_with("Other").not_())
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
