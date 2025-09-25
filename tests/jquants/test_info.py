import datetime

import polars as pl
import pytest
import pytest_asyncio
from polars import DataFrame

from kabukit.jquants.client import JQuantsClient


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
    assert abs((date - datetime.date.today()).days) <= 3  # noqa: DTZ011


@pytest.mark.parametrize(
    ("name", "n"),
    [
        ("Sector17CodeName", 18),
        ("Sector33CodeName", 34),
        ("MarketCodeName", 5),
    ],
)
def test_sector17(df: DataFrame, name: str, n: int) -> None:
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
    from kabukit.jquants.schema import InfoColumns

    assert df.columns == [c.name for c in InfoColumns]


def test_rename(df: DataFrame) -> None:
    from kabukit.jquants.schema import InfoColumns

    df_renamed = InfoColumns.rename(df, strict=True)
    assert df_renamed.columns == [c.value for c in InfoColumns]


@pytest.mark.asyncio
async def test_get_codes() -> None:
    from kabukit.jquants.info import get_codes

    codes = await get_codes()
    assert "72030" in codes
    assert "99840" in codes
