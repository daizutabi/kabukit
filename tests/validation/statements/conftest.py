import pytest
from polars import DataFrame
from polars import col as c

from kabukit.core.statements import Statements
from tests.validation.conftest import pytestmark  # noqa: F401


@pytest.fixture(scope="module")
def data(statements: Statements) -> DataFrame:
    return statements.data


COMMON_COLUMNS = [
    "Date",
    "Time",
    "Code",
    "DisclosureNumber",
    "TypeOfDocument",
    "TypeOfCurrentPeriod",
    "CurrentPeriodStartDate",
    "CurrentPeriodEndDate",
    "CurrentFiscalYearStartDate",
    "CurrentFiscalYearEndDate",
]


@pytest.fixture(
    scope="module",
    params=[
        "NetSales",
        "OperatingProfit",
        "OrdinaryProfit",
        "Profit",
        "EarningsPerShare",
    ],
)
def pl_col(request: pytest.FixtureRequest) -> str:
    """損益計算書のカラム名"""
    return request.param


@pytest.fixture(
    scope="module",
    params=["TotalAssets", "Equity", "EquityToAssetRatio", "BookValuePerShare"],
)
def bs_col(request: pytest.FixtureRequest) -> str:
    """貸借対照表のカラム名"""
    return request.param


@pytest.fixture(
    scope="module",
    params=[
        "CashFlowsFromOperatingActivities",
        "CashFlowsFromInvestingActivities",
        "CashFlowsFromFinancingActivities",
        "CashAndEquivalents",
    ],
)
def cf_col(request: pytest.FixtureRequest) -> str:
    """キャッシュフロー計算書のカラム名"""
    return request.param


@pytest.fixture(scope="module")
def fin(data: DataFrame) -> DataFrame:
    """決算の行だけ抽出する"""
    return data.filter(c.TypeOfDocument.str.contains("Financial"))


@pytest.fixture(scope="module")
def earn_revision(data: DataFrame) -> DataFrame:
    """業績修正の行だけ抽出し、共通カラムと全て欠損のカラムを削除"""
    df = data.filter(c.TypeOfDocument == "EarnForecastRevision")
    cols = [c for c in df.columns if df[c].is_null().all() or c in COMMON_COLUMNS]
    return df.drop(cols)


@pytest.fixture(scope="module")
def dividend_revision(data: DataFrame) -> DataFrame:
    """配当修正の行だけ抽出し、共通カラムと全て欠損のカラムを削除"""
    df = data.filter(c.TypeOfDocument == "DividendForecastRevision")
    cols = [c for c in df.columns if df[c].is_null().all() or c in COMMON_COLUMNS]
    return df.drop(cols)
