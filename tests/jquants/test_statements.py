import datetime

import polars as pl
import pytest
import pytest_asyncio
from polars import DataFrame

from kabukit.jquants.client import JQuantsClient


@pytest_asyncio.fixture(scope="module")
async def client():
    client = JQuantsClient()
    yield client
    await client.aclose()


@pytest_asyncio.fixture(scope="module")
async def df(client: JQuantsClient):
    yield await client.get_statements(date="20250627")


def test_width(df: DataFrame) -> None:
    assert df.width == 75


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


def test_columns(df: DataFrame) -> None:
    from kabukit.jquants.schema import StatementColumns

    assert len(df.columns) == len(StatementColumns)
    assert df.columns == [c.name for c in StatementColumns]


def test_rename(df: DataFrame) -> None:
    from kabukit.jquants.schema import StatementColumns

    df_renamed = StatementColumns.rename(df, strict=True)
    assert df_renamed.columns == [c.value for c in StatementColumns]


@pytest_asyncio.fixture(scope="module")
async def df_7203(client: JQuantsClient):
    yield await client.get_statements("7203")  # Toyota


@pytest.mark.parametrize("prefix", ["1Q", "2Q", "3Q", "FY"])
def test_column_names(df_7203: DataFrame, prefix: str) -> None:
    name = f"{prefix}FinancialStatements_Consolidated_IFRS"
    assert name in df_7203["TypeOfDocument"]


def test_holidays() -> None:
    from kabukit.jquants.statements import get_holidays

    holidays = get_holidays(n=5)
    year = datetime.datetime.now().year  # noqa: DTZ005
    assert holidays[0].year == year - 5
    assert holidays[0].month == 1
    assert holidays[0].day == 1


def test_holidays_year() -> None:
    from kabukit.jquants.statements import get_holidays

    holidays = get_holidays(2000, 5)
    assert holidays[0].year == 1995
    assert holidays[0].month == 1
    assert holidays[0].day == 1


def test_update_effective_date() -> None:
    from datetime import date, time

    from kabukit.jquants.statements import update_effective_date

    df = DataFrame(
        {
            "Date": [
                date(2025, 1, 10),
                date(2025, 1, 10),
                date(2025, 1, 10),
            ],
            "Time": [
                time(9, 0),
                time(15, 30),
                None,
            ],
            "EPS": [1, 2, 3],
        },
    )

    df = update_effective_date(df, 2025)
    x = df["Date"].to_list()
    assert x[0] == date(2025, 1, 10)
    assert x[1] == date(2025, 1, 14)
    assert x[2] == date(2025, 1, 14)


def test_join_asof(df: DataFrame) -> None:
    from datetime import date

    stmt = DataFrame(
        {
            "Date": [
                date(2025, 2, 3),
                date(2025, 2, 6),
            ],
            "EPS": [1, 2],
        },
    )

    price = pl.DataFrame(
        {
            "Date": [
                date(2025, 2, 1),
                date(2025, 2, 2),
                date(2025, 2, 3),
                date(2025, 2, 4),
                date(2025, 2, 5),
                date(2025, 2, 6),
                date(2025, 2, 7),
                date(2025, 2, 8),
            ],
            "Close": [3, 4, 5, 6, 7, 8, 9, 10],
        },
    )

    df = price.join_asof(stmt, on="Date", strategy="backward")
    x = df["EPS"].to_list()
    assert x == [None, None, 1, 1, 1, 2, 2, 2]
