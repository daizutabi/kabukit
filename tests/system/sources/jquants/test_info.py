from __future__ import annotations

import datetime
from zoneinfo import ZoneInfo

import polars as pl
import pytest
import pytest_asyncio

from kabukit.sources.jquants.client import JQuantsClient
from kabukit.sources.jquants.columns import InfoColumns

pytestmark = pytest.mark.system


@pytest.mark.parametrize("only_common_stocks", [True, False])
async def test_date(client: JQuantsClient, *, only_common_stocks: bool) -> None:
    today = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).date()
    date = today - datetime.timedelta(weeks=12)
    df = await client.get_info(date=date, only_common_stocks=only_common_stocks)
    height = 3700 if only_common_stocks else 4_000
    assert df.height > height
    df_date = df.item(0, "Date")
    assert isinstance(df_date, datetime.date)
    assert (df_date - date).days <= 7


async def test_code(client: JQuantsClient) -> None:
    df = await client.get_info(code="7203")
    assert df.height == 1
    name = df.item(0, "Company")
    assert isinstance(name, str)
    assert "トヨタ" in name


@pytest_asyncio.fixture(scope="module")
async def df():
    async with JQuantsClient() as client:
        yield await client.get_info()


def test_width(df: pl.DataFrame) -> None:
    assert df.height > 3700
    assert df.width in [7, 8]  # 7: ライトプラン, 8: スタンダードプラン


@pytest.mark.parametrize(
    ("name", "dtype"),
    [
        ("Date", pl.Date),
        ("Code", pl.String),
        ("Company", pl.String),
        ("Sector17", pl.Categorical),
        ("Sector33", pl.Categorical),
        ("ScaleCategory", pl.Categorical),
        ("Market", pl.Categorical),
        ("Margin", pl.Categorical),
    ],
)
def test_column_dtype(df: pl.DataFrame, name: str, dtype: type) -> None:
    assert df[name].dtype == dtype


def test_today(df: pl.DataFrame) -> None:
    date = df.item(0, "Date")
    assert isinstance(date, datetime.date)
    today = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).date()
    assert abs((date - today).days) <= 7


@pytest.mark.parametrize(
    ("name", "n"),
    [
        ("Sector17", 17),
        ("Sector33", 33),
        ("Market", 3),
        ("Margin", 3),
    ],
)
def test_categorical_column_uniqueness(df: pl.DataFrame, name: str, n: int) -> None:
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
def test_scale_category(df: pl.DataFrame, sc: str) -> None:
    assert sc in df["ScaleCategory"]


def test_columns(df: pl.DataFrame) -> None:
    assert df.columns == [c.name for c in InfoColumns]


def test_rename(df: pl.DataFrame) -> None:
    df_renamed = InfoColumns.rename(df, strict=True)
    assert df_renamed.columns == [c.value for c in InfoColumns]
