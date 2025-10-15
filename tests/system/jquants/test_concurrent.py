import marimo as mo
import pytest
from polars import DataFrame

pytestmark = pytest.mark.system


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

    df = await get(resource, max_items=3, callback=callback)
    assert df["Code"].n_unique() == 3


@pytest.mark.asyncio
async def test_get_target_codes() -> None:
    from kabukit.jquants.concurrent import get_target_codes

    codes = await get_target_codes()
    assert "72030" in codes
    assert "99840" in codes


@pytest.mark.asyncio
async def test_get_target_codes_all_ends_with_zero() -> None:
    from kabukit.jquants.concurrent import get_target_codes

    codes = await get_target_codes()
    assert all(code.endswith("0") for code in codes)


@pytest.mark.asyncio
async def test_get_statements() -> None:
    from kabukit.jquants.concurrent import get_statements

    df = await get_statements(["7203", "6758"])
    assert sorted(df["Code"].unique()) == ["67580", "72030"]


@pytest.mark.asyncio
async def test_get_statements_with_max_items() -> None:
    from kabukit.jquants.concurrent import get_statements

    df = await get_statements(["7203", "6758"], max_items=1)
    assert df["Code"].unique().to_list() == ["72030"]


@pytest.mark.asyncio
async def test_get_statements_without_codes() -> None:
    from kabukit.jquants.concurrent import get_statements

    df = await get_statements(max_items=3)
    assert df["Code"].n_unique() == 3


@pytest.mark.asyncio
async def test_get_statements_with_single_code() -> None:
    from kabukit.jquants.concurrent import get_statements

    df = await get_statements("7203")
    assert df["Code"].unique().to_list() == ["72030"]


@pytest.mark.asyncio
async def test_get_prices() -> None:
    from kabukit.jquants.concurrent import get_prices

    df = await get_prices(["7203", "6758"])
    assert sorted(df["Code"].unique()) == ["67580", "72030"]


@pytest.mark.asyncio
async def test_get_prices_with_max_items() -> None:
    from kabukit.jquants.concurrent import get_prices

    df = await get_prices(["7203", "6758"], max_items=1)
    assert df["Code"].unique().to_list() == ["72030"]


@pytest.mark.asyncio
async def test_get_prices_without_codes() -> None:
    from kabukit.jquants.concurrent import get_prices

    df = await get_prices(max_items=3)
    assert df["Code"].n_unique() == 3


@pytest.mark.asyncio
async def test_get_prices_with_single_code() -> None:
    from kabukit.jquants.concurrent import get_prices

    df = await get_prices("7203")
    assert df["Code"].unique().to_list() == ["72030"]
