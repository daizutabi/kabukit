from __future__ import annotations

from datetime import date

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from kabukit.sources.edinet.batch import get_documents, get_list

pytestmark = pytest.mark.system


def callback(df: pl.DataFrame) -> pl.DataFrame:
    assert isinstance(df, pl.DataFrame)
    return df


async def test_get_list_single_date() -> None:
    df = await get_list("2025-10-09")
    dates = df["Date"].unique().to_list()

    assert dates == [
        date(2025, 9, 29),
        date(2025, 9, 30),
        date(2025, 10, 9),
        date(2025, 10, 10),
    ]


async def test_get_list_multiple_dates() -> None:
    df = await get_list(["2025-10-09", "2025-10-10"])
    expected = [
        date(2025, 9, 29),
        date(2025, 9, 30),
        date(2025, 10, 9),
        date(2025, 10, 10),
        date(2025, 10, 14),
    ]
    assert sorted(df["Date"].unique().to_list()) == expected


async def test_get_list_without_dates() -> None:
    df = await get_list(days=7, max_items=6, callback=callback)
    assert df.width == 25


async def test_get_documents_csv() -> None:
    df = await get_list(["2025-09-09", "2025-09-19", "2025-09-22"])
    doc_ids = df.filter(CsvFlag=True).get_column("DocumentId").sort()
    df = await get_documents(doc_ids, max_items=10, callback=callback)
    assert df["DocumentId"].n_unique() == 10


async def test_get_documents_pdf() -> None:
    df = await get_list("2025-09-09")
    doc_ids = df.filter(PdfFlag=True).get_column("DocumentId").to_list()
    df = await get_documents(doc_ids, max_items=2, pdf=True)
    assert df.shape == (2, 2)
    for i in range(2):
        pdf = df.item(i, "PdfContent")
        assert isinstance(pdf, bytes)
        assert pdf.startswith(b"%PDF-")


async def test_get_documents_single_doc_id() -> None:
    df = await get_list("2025-09-09")
    doc_id = df.filter(CsvFlag=True).get_column("DocumentId").first()
    assert isinstance(doc_id, str)
    df = await get_documents(doc_id)
    assert df["DocumentId"].n_unique() == 1
    assert df.item(0, "DocumentId") == doc_id


async def test_get_documents_invalid_id() -> None:
    df = await get_documents("E00000")
    assert_frame_equal(df, pl.DataFrame())
