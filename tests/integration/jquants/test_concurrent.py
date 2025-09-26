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
async def test_fetch(resource: str) -> None:
    from kabukit.jquants.concurrent import fetch

    df = await fetch(resource, ["7203", "6758"], progress=mo.status.progress_bar)
    assert sorted(df["Code"].unique()) == ["67580", "72030"]


@pytest.mark.asyncio
async def test_fetch_all(resource: str) -> None:
    from kabukit.jquants.concurrent import fetch_all

    df = await fetch_all(resource, limit=3, callback=callback)
    assert df["Code"].n_unique() == 3