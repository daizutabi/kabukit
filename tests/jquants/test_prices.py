import polars as pl
import pytest
import pytest_asyncio
from polars import DataFrame

from kabukit.jquants.client import JQuantsClient


@pytest_asyncio.fixture(scope="module")
async def df():
    client = JQuantsClient()
    yield await client.get_prices("3671")
    await client.aclose()


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
        ("AdjustmentOpen", pl.Float64),
        ("AdjustmentHigh", pl.Float64),
        ("AdjustmentLow", pl.Float64),
        ("AdjustmentClose", pl.Float64),
        ("AdjustmentVolume", pl.Float64),
    ],
)
def test_column_dtype(df: DataFrame, name: str, dtype: type) -> None:
    assert df[name].dtype == dtype


def test_turnover_volume(df: DataFrame) -> None:
    a = df["TurnoverValue"]
    b = df["High"] * df["Volume"]
    c = df["Low"] * df["Volume"]
    assert (a <= b).all()
    assert (a >= c).all()
