import pytest
from polars import DataFrame

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_fetch() -> None:
    from kabukit.edinet.concurrent import get

    df = await get("documents", ["2025-09-09", "2025-09-19", "2025-09-22"])
    assert df.shape == (1231, 30)
    assert df["Date"].n_unique() == 3
    assert df["docID"].n_unique() == 1229  # 重複あり


def callback(df: DataFrame) -> DataFrame:
    assert isinstance(df, DataFrame)
    return df


@pytest.mark.asyncio
async def test_fetch_documents() -> None:
    from kabukit.edinet.concurrent import get_documents

    df = await get_documents(7, limit=6, callback=callback)
    assert df.width == 30


@pytest.mark.asyncio
async def test_fetch_csv() -> None:
    from kabukit.edinet.concurrent import get, get_csv

    df = await get("documents", ["2025-09-09", "2025-09-19", "2025-09-22"])
    doc_ids = df.filter(csvFlag=True).get_column("docID").sort()
    df = await get_csv(doc_ids, limit=10, callback=callback)
    assert df["docID"].n_unique() == 10
