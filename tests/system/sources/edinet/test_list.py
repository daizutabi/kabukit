from __future__ import annotations

import datetime

import polars as pl
import pytest
import pytest_asyncio

from kabukit.sources.edinet.client import EdinetClient

pytestmark = pytest.mark.system


@pytest.mark.asyncio
async def test_list(client: EdinetClient) -> None:
    df = await client.get_list("2025-09-04")
    assert df.shape == (76, 25)
    assert df.columns[0] == "Date"
    assert df["Date"].dtype == pl.Date
    assert df.columns[-1] == "FileDate"
    assert df["FileDate"].dtype == pl.Date
    assert df["FileDate"].unique().to_list() == [datetime.date(2025, 9, 4)]


@pytest.mark.asyncio
async def test_list_invalid_date(client: EdinetClient) -> None:
    df = await client.get_list("1000-01-01")
    assert df.shape == (0, 0)


@pytest.mark.asyncio
async def test_list_holiday(client: EdinetClient) -> None:
    df = await client.get_list("2025-09-23")
    assert df.shape == (0, 0)


@pytest.mark.asyncio
async def test_pdf(client: EdinetClient) -> None:
    df = await client.get_pdf("S100WKHJ")
    content = df.item(0, "PdfContent")
    assert isinstance(content, bytes)
    assert content.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_pdf_error(client: EdinetClient) -> None:
    with pytest.raises(ValueError, match="PDF is not available"):
        await client.get_pdf("S100WMS8")


@pytest.mark.asyncio
async def test_zip(client: EdinetClient) -> None:
    assert await client.get_zip("S100WKHJ", doc_type=5) is not None


@pytest.mark.asyncio
async def test_zip_error(client: EdinetClient) -> None:
    with pytest.raises(ValueError, match="ZIP is not available"):
        await client.get_zip("S100WM0M", doc_type=5)


@pytest.mark.asyncio
async def test_csv(client: EdinetClient) -> None:
    df = await client.get_csv("S100WKHJ")
    assert df.columns[0] == "DocumentId"
    assert df.shape == (47, 10)
    assert "値" in df.columns


@pytest_asyncio.fixture(scope="module")
async def df():
    client = EdinetClient()
    yield await client.get_list("2025-06-27")
    await client.aclose()


def test_df_xbrl_csv(df: pl.DataFrame) -> None:
    df = df.filter(XbrlFlag="1")
    assert df.height == df.filter(CsvFlag="1").height


def test_df_xbrl_pdf(df: pl.DataFrame) -> None:
    df = df.filter(XbrlFlag="1")
    assert df.height == df.filter(PdfFlag="1").height


def test_columns(df: pl.DataFrame) -> None:
    from kabukit.sources.edinet.columns import ListColumns

    assert df.columns == [c.name for c in ListColumns]


def test_rename(df: pl.DataFrame) -> None:
    from kabukit.sources.edinet.columns import ListColumns

    df_renamed = ListColumns.rename(df, strict=True)
    assert df_renamed.columns == [c.value for c in ListColumns]
