import marimo as mo
import pytest
from polars import DataFrame

pytestmark = pytest.mark.integration


@pytest.fixture(params=["statements", "prices"])
def resource(request: pytest.FixtureRequest) -> str:
    return request.param


def callback(df: DataFrame) -> None:
    assert isinstance(df, DataFrame)


@pytest.mark.asyncio
async def test_get(resource: str) -> None:
    from kabukit.jquants.concurrent import get

    df = await get(resource, ["7203", "6758"], progress=mo.status.progress_bar)
    assert sorted(df["Code"].unique()) == ["67580", "72030"]


@pytest.mark.asyncio
async def test_get_without_codes(resource: str) -> None:
    from kabukit.jquants.concurrent import get

    df = await get(resource, limit=3, callback=callback)
    assert df["Code"].n_unique() == 3
