import polars as pl
import pytest
import pytest_asyncio
from polars import DataFrame

from kabukit.jquants.client import JQuantsClient


@pytest_asyncio.fixture(scope="module")
async def client():
    async with JQuantsClient() as client:
        yield client


@pytest_asyncio.fixture(scope="module")
async def df(client: JQuantsClient):
    yield await client.get_statements(date="20250627")


@pytest.mark.integration
def test_width(df: DataFrame) -> None:
    assert df.width == 75


@pytest.mark.integration
@pytest.mark.parametrize(
    ("name", "dtype"),
    [
        ("Date", pl.Date),
        ("Time", pl.Time),
        ("Code", pl.String),
        ("DisclosureNumber", pl.String),
        ("TypeOfDocument", pl.String),
        ("TypeOfCurrentPeriod", pl.Categorical),
        ("CurrentPeriodStartDate", pl.Date),
        ("CurrentPeriodEndDate", pl.Date),
        ("CurrentFiscalYearStartDate", pl.Date),
        ("CurrentFiscalYearEndDate", pl.Date),
        ("NextFiscalYearStartDate", pl.Date),
        ("NextFiscalYearEndDate", pl.Date),
    ],
)
def test_column_dtype(df: DataFrame, name: str, dtype: type) -> None:
    assert df[name].dtype == dtype


@pytest.mark.integration
def test_columns(df: DataFrame) -> None:
    from kabukit.jquants.schema import StatementColumns

    assert len(df.columns) == len(StatementColumns)
    assert df.columns == [c.name for c in StatementColumns]


@pytest.mark.integration
def test_rename(df: DataFrame) -> None:
    from kabukit.jquants.schema import StatementColumns

    df_renamed = StatementColumns.rename(df, strict=True)
    assert df_renamed.columns == [c.value for c in StatementColumns]


@pytest_asyncio.fixture(scope="module")
async def df_7203(client: JQuantsClient):
    yield await client.get_statements("7203")  # Toyota


@pytest.mark.integration
@pytest.mark.parametrize("prefix", ["1Q", "2Q", "3Q", "FY"])
def test_column_names(df_7203: DataFrame, prefix: str) -> None:
    name = f"{prefix}FinancialStatements_Consolidated_IFRS"
    assert name in df_7203["TypeOfDocument"]
