"""Statementsデータの項目仕様（TypeOfDocument別）

このドキュメントは、TypeOfDocumentの値に応じて、どの項目にデータが含まれるか（not null）、
含まれないか（null）を定義する。

凡例:
- o: ほとんどのケースで値が存在する (not null)
- x: ほとんどのケースで値が存在しない (null)

---

1. 決算短信 (FinancialStatements)

| 項目カテゴリ | 1Q | 2Q | 3Q | FY (通期) |
|:---|:---:|:---:|:---:|:---:|
| 実績 (P/L) | o | o | o | o |
| 実績 (B/S) | o | o | o | o |
| 実績 (C/F) | o | o | o | o |
| 配当実績 | x | o | x | o |
| 通期業績予想 | o | o | o | o |
| 配当予想 | o | o | o | o |

- P/L: NetSales, OperatingProfit, Profit など
- B/S: TotalAssets, Equity など
- C/F: CashFlows...（四半期C/Fは開示が任意な場合がある）
- 配当実績: 2Qと期末(FY)の実績が主。

---

2. 予想修正 (EarnForecastRevision, DividendForecastRevision)

| 項目カテゴリ | 業績予想修正 | 配当予想修正 |
|:---|:---:|:---:|
| 実績 (P/L, B/S, C/F) | x | x |
| 配当実績 | x | x |
| 通期業績予想 | o | x |
| 配当予想 | x | o |

- 予想修正のレポートは、修正対象の項目のみを含み、実績値は含まない。

"""

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


@pytest.mark.parametrize(
    "column",
    [c for c in COMMON_COLUMNS if c not in ["Time"]],
)
def test_is_not_null_all(data: DataFrame, column: str) -> None:
    """共通カラムのうち、Time以外は全て非欠損"""
    assert data[column].is_not_null().all()


@pytest.mark.parametrize("column", ["Time"])
def test_is_not_null_any(data: DataFrame, column: str) -> None:
    """Timeカラムは一部非欠損"""
    assert data[column].is_not_null().any()


@pytest.fixture(scope="module")
def tod(data: DataFrame) -> Series:
    """TypeOfDocumentのユニークな値一覧"""
    return data["TypeOfDocument"].unique()


@pytest.fixture(scope="module")
def tod_fin(tod: Series) -> Series:
    """TypeOfDocumentのうち、決算関連のものだけ抽出"""
    return tod.filter(tod.str.contains("Financial"))


def test_type_of_document_financial_period(tod_fin: Series) -> None:
    """決算の期間は、(1Q, 2Q, 3Q, FY, OtherPeriod)"""
    x = tod_fin.str.split("Financial").list.first().unique()
    assert sorted(x) == ["1Q", "2Q", "3Q", "FY", "OtherPeriod"]


def test_type_of_document_financial_consolidated(tod_fin: Series) -> None:
    """決算の連結・非連結の区分は、(Consolidated, NonConsolidated)"""
    x = tod_fin.str.split("_").list[1].unique()
    assert sorted(x) == ["Consolidated", "NonConsolidated"]


def test_type_of_document_financial_type(tod_fin: Series) -> None:
    """決算の会計基準は、(JP, US, IFRS, Foreign)"""
    x = tod_fin.str.split("_").list.last().unique()
    assert sorted(x) == ["Foreign", "IFRS", "JP", "US"]


def test_type_of_document_dividend_and_earn_forecast(tod: Series) -> None:
    """決算以外のTypeOfDocumentは、(DividendForecastRevision, EarnForecastRevision)"""
    x = tod.filter(tod.str.contains("Financial").not_()).unique()
    assert sorted(x) == ["DividendForecastRevision", "EarnForecastRevision"]


def test_type_of_document_other_period(tod_fin: Series) -> None:
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
    data: DataFrame,
    name: str,
    length: int,
) -> None:
    """OtherPeriodFinancialStatementsの種類ごとの件数を確認。今後増える可能性がある。"""
    assert data.filter(c.TypeOfDocument == name).height == length


@pytest.mark.parametrize(
    "column",
    ["NextFiscalYearStartDate", "NextFiscalYearEndDate"],
)
def test_next_fiscal_year_start_end(data: DataFrame, column: str) -> None:
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


@pytest.mark.parametrize("period", ["1Q", "2Q", "3Q", "FY"])
def test_fin_current_period_equality(fin: DataFrame, period: str) -> None:
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
def test_fin_current_period_days(fin: DataFrame, period: str, days: int) -> None:
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
    assert 0.995 < x <= 1


def test_fin_profit_loss(fin: DataFrame, pl_col: str) -> None:
    """決算の損益計算書の各項目は、ほぼ100%埋まっている"""
    x = fin[pl_col].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.94 < x <= 1.0  # 割合 1 に近い


@pytest.mark.parametrize("kind", ["US", "IFRS"])
def test_fin_ordinary_profit(fin: DataFrame, kind: str) -> None:
    """US・IFRS基準の決算では、OrdinaryProfitはほとんど存在しない"""
    df = fin.filter(c.TypeOfDocument.str.contains(kind))
    x = df["OrdinaryProfit"].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.0 < x <= 0.025  # ごく一部のみ


def test_fin_diluted_earnings_per_share(fin: DataFrame) -> None:
    """DilutedEarningsPerShareは、30%程度が埋まっている"""
    x = fin["DilutedEarningsPerShare"].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.30 < x <= 0.31  # 30% くらい


def test_fin_balance_sheet(fin: DataFrame, bs_col: str) -> None:
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
        ("OtherPeriod", 0.80, 0.85),
    ],
)
def test_fin_cash_flow(
    fin: DataFrame,
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
    fin: DataFrame,
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
    fin: DataFrame,
    column: str,
    low: float,
    high: float,
) -> None:
    """通期決算では、年間配当実績がほぼ埋まっている"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("FY"))
    x = df[column].is_not_null().mean()
    assert isinstance(x, float)
    assert low <= x <= high


def test_fin_result_dividend_other_period(fin: DataFrame) -> None:
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
    fin: DataFrame,
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
        ("ForecastTotalDividendPaidAnnual", 0, 0),
        ("ForecastPayoutRatioAnnual", 0, 0),
    ],
)
def test_fin_forecast_dividend_annual(
    fin: DataFrame,
    column: str,
    low: float,
    high: float,
) -> None:
    """通期決算以外では、年間配当予想がある程度埋まっている"""
    df = fin.filter(~c.TypeOfDocument.str.starts_with("FY"))
    x = df[column].is_not_null().mean()
    assert isinstance(x, float)
    assert low <= x <= high


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
    fin: DataFrame,
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
    fin: DataFrame,
    column: str,
    low: float,
    high: float,
) -> None:
    """FY決算では、次期の年間配当予想がある程度埋まっている"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("FY"))
    x = df[column].is_not_null().mean()
    assert isinstance(x, float)
    assert low <= x <= high


def test_fin_next_year_forecast(fin: DataFrame) -> None:
    """FY決算以外では、次期の予想は存在しない"""
    df = fin.filter(~c.TypeOfDocument.str.starts_with("FY")).select(
        pl.col("^NextYear.*$"),
    )
    assert all(df[c].is_null().all() for c in df.columns)


def test_fin_forecast(fin: DataFrame) -> None:
    """FY決算では、当期の予想は存在しない。ただし、誤登録の可能性あり"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("FY")).select(
        pl.col("^Forecast.*$"),
    )
    x = [df[c].is_null().mean() for c in df.columns]
    x = [x for x in x if isinstance(x, float)]
    assert len(x) == 27
    assert all(0.999 < v <= 1.0 for v in x)


def test_fin_forecast_other(fin: DataFrame) -> None:
    """OtherPeriod決算では、当期の予想は存在しない"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("OtherPeriod")).select(
        pl.col("^Forecast.*$"),
    )
    assert all(df[c].is_null().all() for c in df.columns)


@pytest.mark.parametrize(
    ("period", "low", "high"),
    [
        ("1Q", 0.54, 0.57),
        ("2Q", 0.0, 2e-4),  # 誤登録の可能性あり
        ("3Q", 0.0, 4e-5),  # 誤登録の可能性あり
        ("FY", 0.0, 0.0),
    ],
)
def test_fin_forecast_profit_loss_2nd_quarter(
    fin: DataFrame,
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
    fin: DataFrame,
    pl_col: str,
) -> None:
    """FY決算では、次期の2Q業績予想の損益計算書の各項目が50%程度埋まっている"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("FY"))
    x = df[f"NextYearForecast{pl_col}2ndQuarter"].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.50 <= x <= 0.55


def test_fin_forecast_profit_loss(fin: DataFrame, pl_col: str) -> None:
    """FY決算以外では、期末業績予想の損益計算書の各項目が90%程度埋まっている"""
    df = fin.filter(
        ~c.TypeOfDocument.str.starts_with("FY"),
        ~c.TypeOfDocument.str.starts_with("OtherPeriod"),
    )
    x = df[f"Forecast{pl_col}"].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.86 <= x <= 0.95


def test_fin_next_year_forecast_profit_loss(fin: DataFrame, pl_col: str) -> None:
    """FY決算では、次期の期末業績予想の損益計算書の各項目が85%程度埋まっている"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("FY"))
    x = df[f"NextYearForecast{pl_col}"].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.80 <= x <= 0.90


@pytest.mark.parametrize("period", ["1Q", "2Q", "3Q", "FY"])
@pytest.mark.parametrize(
    "column",
    ["NumberOfShares", "NumberOfTreasuryStock", "AverageNumberOfShares"],
)
def test_fin_number_of_shares(fin: DataFrame, period: str, column: str) -> None:
    """決算の株式数は、ほぼ100%埋まっている"""
    df = fin.filter(c.TypeOfDocument.str.starts_with(period))
    x = df[column].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.94 < x <= 1.0  # 割合 1 に近い


@pytest.mark.parametrize(
    "column",
    ["NumberOfShares", "NumberOfTreasuryStock", "AverageNumberOfShares"],
)
def test_fin_number_of_shares_other(fin: DataFrame, column: str) -> None:
    """OtherPeriod決算では、株式数は存在しない"""
    df = fin.filter(c.TypeOfDocument.str.starts_with("OtherPeriod"))
    assert df[column].is_null().all()


@pytest.fixture(scope="module")
def earn_revision(data: DataFrame) -> DataFrame:
    """業績修正の行だけ抽出し、共通カラムと全て欠損のカラムを削除"""
    df = data.filter(c.TypeOfDocument == "EarnForecastRevision")
    cols = [c for c in df.columns if df[c].is_null().all() or c in COMMON_COLUMNS]
    return df.drop(cols)


def test_earn_revision_width(earn_revision: DataFrame) -> None:
    assert earn_revision.width == 25


def test_earn_revision_column_name_starts_with_forecast(
    earn_revision: DataFrame,
) -> None:
    """業績修正のカラム名が "Forecast" で始まる"""
    assert all(c.startswith("Forecast") for c in earn_revision.columns)


def test_earn_revision_profit_loss_fiscal_year_end(
    earn_revision: DataFrame,
    pl_col: str,
) -> None:
    """業績修正の期末業績予想の損益項目の各項目がどの程度埋まっているか"""
    x = earn_revision[f"Forecast{pl_col}"].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.65 < x < 0.70  # 割合 3/4 くらい


def test_earn_revision_profit_loss_2nd_quarter(
    earn_revision: DataFrame,
    pl_col: str,
) -> None:
    """業績修正の2Q業績予想の損益項目の各項目がどの程度埋まっているか"""
    x = earn_revision[f"Forecast{pl_col}2ndQuarter"].is_not_null().mean()
    assert isinstance(x, float)
    assert 0.27 < x < 0.29  # 割合 1/4 くらい


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
    earn_revision: DataFrame,
    name: str,
    high: float,
    low: float,
) -> None:
    """業績修正の配当予想の各項目がどの程度埋まっているか"""
    x = earn_revision[f"ForecastDividendPerShare{name}"].is_not_null().mean()
    assert isinstance(x, float)
    assert low < x < high


@pytest.fixture(scope="module")
def dividend_revision(data: DataFrame) -> DataFrame:
    """配当修正の行だけ抽出し、共通カラムと全て欠損のカラムを削除"""
    df = data.filter(c.TypeOfDocument == "DividendForecastRevision")
    cols = [c for c in df.columns if df[c].is_null().all() or c in COMMON_COLUMNS]
    return df.drop(cols)


def test_dividend_revision_width(dividend_revision: DataFrame) -> None:
    assert dividend_revision.width == 5


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
    dividend_revision: DataFrame,
    name: str,
    high: float,
    low: float,
) -> None:
    """配当修正の配当予想の各項目がどの程度埋まっているか"""
    x = dividend_revision[f"ForecastDividendPerShare{name}"].is_not_null().mean()
    assert isinstance(x, float)
    assert low < x < high
