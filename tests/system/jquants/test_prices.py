from __future__ import annotations

import datetime

import polars as pl
import pytest
import pytest_asyncio
from polars import DataFrame

from kabukit.sources.jquants.client import JQuantsClient

pytestmark = pytest.mark.system


@pytest.mark.asyncio
async def test_code(client: JQuantsClient) -> None:
    df = await client.get_prices(code="7203")
    assert df.width == 16


@pytest.mark.asyncio
async def test_date(client: JQuantsClient) -> None:
    df = await client.get_prices(date="2025-08-29")
    assert df.height > 4000
    assert df.height == df["Code"].n_unique()


@pytest.mark.asyncio
async def test_empty(client: JQuantsClient) -> None:
    df = await client.get_prices(date="2025-08-30")
    assert df.shape == (0, 0)


@pytest.mark.asyncio
async def test_from_to(client: JQuantsClient) -> None:
    df = await client.get_prices(code="7203", from_="2025-08-16", to="2025-08-25")
    assert df.height == 6
    assert df.item(0, "Date") == datetime.date(2025, 8, 18)
    assert df.item(5, "Date") == datetime.date(2025, 8, 25)


@pytest.mark.asyncio
async def test_from(client: JQuantsClient) -> None:
    df = await client.get_prices(code="7203", from_="2025-08-16")
    assert df.item(0, "Date") == datetime.date(2025, 8, 18)


@pytest.mark.asyncio
async def test_to(client: JQuantsClient) -> None:
    df = await client.get_prices(code="7203", to="2025-08-16")
    assert df.item(-1, "Date") == datetime.date(2025, 8, 15)


@pytest.mark.asyncio
async def test_without_code(client: JQuantsClient) -> None:
    df = await client.get_prices()
    assert df.height > 3000


@pytest.mark.asyncio
async def test_latest_available_prices(client: JQuantsClient) -> None:
    df = await client.get_latest_available_prices()
    assert df.height > 3000


@pytest.mark.asyncio
async def test_latest_available_prices_empty(client: JQuantsClient) -> None:
    df = await client.get_latest_available_prices(0)
    assert df.is_empty()


@pytest_asyncio.fixture(scope="module")
async def df():
    async with JQuantsClient() as client:
        yield await client.get_prices("3671")


def test_width(df: DataFrame) -> None:
    assert df.width == 16


@pytest.mark.parametrize(
    ("name", "dtype"),
    [
        ("Date", pl.Date),
        ("Code", pl.String),
        ("Open", pl.Float64),
        ("High", pl.Float64),
        ("Low", pl.Float64),
        ("Close", pl.Float64),
        ("UpperLimit", pl.Boolean),
        ("LowerLimit", pl.Boolean),
        ("Volume", pl.Float64),
        ("TurnoverValue", pl.Float64),
        ("AdjustmentFactor", pl.Float64),
        ("RawOpen", pl.Float64),
        ("RawHigh", pl.Float64),
        ("RawLow", pl.Float64),
        ("RawClose", pl.Float64),
        ("RawVolume", pl.Float64),
    ],
)
def test_column_dtype(df: DataFrame, name: str, dtype: type) -> None:
    assert df[name].dtype == dtype


def test_turnover_value(df: DataFrame) -> None:
    a = df["TurnoverValue"]
    b = df["RawHigh"] * df["RawVolume"]
    c = df["RawLow"] * df["RawVolume"]
    assert (a <= b).all()
    assert (a >= c).all()


def test_columns(df: DataFrame) -> None:
    from kabukit.sources.jquants.schema import PriceColumns

    assert df.columns == [c.name for c in PriceColumns]


def test_rename(df: DataFrame) -> None:
    from kabukit.sources.jquants.schema import PriceColumns

    df_renamed = PriceColumns.rename(df, strict=True)
    assert df_renamed.columns == [c.value for c in PriceColumns]
