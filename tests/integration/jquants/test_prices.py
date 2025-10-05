import polars as pl
import pytest
import pytest_asyncio
from polars import DataFrame

from kabukit.jquants.client import JQuantsClient

pytestmark = pytest.mark.integration


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
    from kabukit.jquants.schema import PriceColumns

    assert df.columns == [c.name for c in PriceColumns]


def test_rename(df: DataFrame) -> None:
    from kabukit.jquants.schema import PriceColumns

    df_renamed = PriceColumns.rename(df, strict=True)
    assert df_renamed.columns == [c.value for c in PriceColumns]
