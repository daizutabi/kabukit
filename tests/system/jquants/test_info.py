import datetime
from zoneinfo import ZoneInfo

import polars as pl
import pytest
import pytest_asyncio
from polars import DataFrame

from kabukit.sources.jquants.client import JQuantsClient

pytestmark = pytest.mark.system


@pytest.mark.asyncio
async def test_date(client: JQuantsClient) -> None:
    today = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).date()
    date = today - datetime.timedelta(weeks=12)
    df = await client.get_info(date=date)
    assert df.height > 4000
    df_date = df.item(0, "Date")
    assert isinstance(df_date, datetime.date)
    assert (df_date - date).days <= 7


@pytest.mark.asyncio
async def test_code(client: JQuantsClient) -> None:
    df = await client.get_info(code="7203")
    assert df.height == 1
    name = df.item(0, "CompanyName")
    assert isinstance(name, str)
    assert "トヨタ" in name


@pytest_asyncio.fixture(scope="module")
async def df():
    async with JQuantsClient() as client:
        yield await client.get_info()


def test_width(df: DataFrame) -> None:
    assert df.height > 4000
    assert df.width in [7, 8]  # 7: ライトプラン, 8: スタンダードプラン


@pytest.mark.parametrize(
    ("name", "dtype"),
    [
        ("Date", pl.Date),
        ("Code", pl.String),
        ("CompanyName", pl.String),
        ("Sector17CodeName", pl.Categorical),
        ("Sector33CodeName", pl.Categorical),
        ("ScaleCategory", pl.Categorical),
        ("MarketCodeName", pl.Categorical),
    ],
)
def test_column_dtype(df: DataFrame, name: str, dtype: type) -> None:
    assert df[name].dtype == dtype


def test_today(df: DataFrame) -> None:
    date = df.item(0, "Date")
    assert isinstance(date, datetime.date)
    today = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).date()
    assert abs((date - today).days) <= 7


@pytest.mark.parametrize(
    ("name", "n"),
    [
        ("Sector17CodeName", 18),
        ("Sector33CodeName", 34),
        ("MarketCodeName", 5),
    ],
)
def test_categorical_column_uniqueness(df: DataFrame, name: str, n: int) -> None:
    assert df[name].n_unique() == n


@pytest.mark.parametrize(
    "sc",
    [
        "-",
        "TOPIX Small 1",
        "TOPIX Core30",
        "TOPIX Mid400",
        "TOPIX Small 2",
        "TOPIX Large70",
    ],
)
def test_scale_category(df: DataFrame, sc: str) -> None:
    assert sc in df["ScaleCategory"]


def test_columns(df: DataFrame) -> None:
    from kabukit.sources.jquants.schema import InfoColumns

    assert df.columns == [c.name for c in InfoColumns]


def test_rename(df: DataFrame) -> None:
    from kabukit.sources.jquants.schema import InfoColumns

    df_renamed = InfoColumns.rename(df, strict=True)
    assert df_renamed.columns == [c.value for c in InfoColumns]
