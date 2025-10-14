from datetime import date

import pytest
from polars import DataFrame

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_get() -> None:
    from kabukit.edinet.concurrent import get

    df = await get("entries", ["2025-09-09", "2025-09-19", "2025-09-22"])
    assert df.shape == (1231, 30)
    assert df["Date"].n_unique() == 3
    assert df["docID"].n_unique() == 1229  # 重複あり


def callback(df: DataFrame) -> DataFrame:
    assert isinstance(df, DataFrame)
    return df


@pytest.mark.asyncio
async def test_get_entries_dates() -> None:
    from kabukit.edinet.concurrent import get_entries

    df = await get_entries(["2025-10-09", "2025-10-10"])
    expected = [date(2025, 10, 9), date(2025, 10, 10)]
    assert sorted(df["Date"].unique().to_list()) == expected


@pytest.mark.asyncio
async def test_get_entries_single_date() -> None:
    from kabukit.edinet.concurrent import get_entries

    df = await get_entries("2025-10-09")
    dates = df["Date"].unique().to_list()
    assert len(dates) == 1
    assert dates[0] == date(2025, 10, 9)


@pytest.mark.asyncio
async def test_get_entries_without_dates() -> None:
    from kabukit.edinet.concurrent import get_entries

    df = await get_entries(days=7, limit=6, callback=callback)
    assert df.width == 30


@pytest.mark.asyncio
async def test_get_documents_csv() -> None:
    from kabukit.edinet.concurrent import get_documents, get_entries

    df = await get_entries(["2025-09-09", "2025-09-19", "2025-09-22"])
    doc_ids = df.filter(csvFlag=True).get_column("docID").sort()
    df = await get_documents(doc_ids, limit=10, callback=callback)
    assert df["docID"].n_unique() == 10


@pytest.mark.asyncio
async def test_get_documents_pdf() -> None:
    from kabukit.edinet.concurrent import get_documents, get_entries

    df = await get_entries("2025-09-09")
    doc_ids = df.filter(pdfFlag=True).get_column("docID").to_list()
    df = await get_documents(doc_ids, limit=2, pdf=True)
    assert df.shape == (2, 2)
    for i in range(2):
        pdf = df.item(i, "pdf")
        assert isinstance(pdf, bytes)
        assert pdf.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_get_documents_single_doc_id() -> None:
    from kabukit.edinet.concurrent import get_documents, get_entries

    df = await get_entries("2025-09-09")
    doc_id = df.filter(csvFlag=True).get_column("docID").first()
    assert isinstance(doc_id, str)
    df = await get_documents(doc_id)
    assert df["docID"].n_unique() == 1
    assert df.item(0, "docID") == doc_id


@pytest.mark.asyncio
async def test_get_documents_invalid_id_raises_error() -> None:
    from kabukit.edinet.concurrent import get_documents

    with pytest.raises(ValueError, match="ZIP is not available"):
        await get_documents("E00000")
