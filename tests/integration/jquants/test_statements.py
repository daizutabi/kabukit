import polars as pl
import pytest
import pytest_asyncio
from polars import DataFrame

from kabukit.jquants.client import JQuantsClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_code(client: JQuantsClient) -> None:
    df = await client.get_statements(code="7203")
    assert df.width == 105


@pytest.mark.asyncio
async def test_date(client: JQuantsClient) -> None:
    df = await client.get_statements(date="2025-08-29")
    assert df.height == 18


@pytest.mark.asyncio
async def test_empty(client: JQuantsClient) -> None:
    df = await client.get_statements(date="2025-08-30")
    assert df.shape == (0, 0)


@pytest_asyncio.fixture(scope="module")
async def df():
    async with JQuantsClient() as client:
        yield await client.get_statements(date="20250627")


def test_width(df: DataFrame) -> None:
    assert df.width == 105


@pytest.mark.parametrize(
    ("name", "dtype"),
    [
        ("Date", pl.Date),
        ("DisclosedDate", pl.Date),
        ("DisclosedTime", pl.Time),
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


def test_columns(df: DataFrame) -> None:
    from kabukit.jquants.schema import StatementColumns

    assert len(df.columns) == len(StatementColumns)
    assert df.columns == [c.name for c in StatementColumns]


def test_rename(df: DataFrame) -> None:
    from kabukit.jquants.schema import StatementColumns

    df_renamed = StatementColumns.rename(df, strict=True)
    assert df_renamed.columns == [c.value for c in StatementColumns]


@pytest.mark.asyncio
@pytest.mark.parametrize("prefix", ["1Q", "2Q", "3Q", "FY"])
async def test_column_names(prefix: str) -> None:
    async with JQuantsClient() as client:
        df = await client.get_statements("7203")  # Toyota
    name = f"{prefix}FinancialStatements_Consolidated_IFRS"
    assert name in df["TypeOfDocument"]
