import polars as pl
import pytest
import pytest_asyncio
from polars import DataFrame

from kabukit.edinet.client import EdinetClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_count(client: EdinetClient) -> None:
    assert await client.get_count("2025-09-05") > 0


@pytest.mark.asyncio
async def test_count_zero(client: EdinetClient) -> None:
    assert await client.get_count("1000-01-01") == 0


@pytest.mark.asyncio
async def test_count_status_not_200(client: EdinetClient) -> None:
    assert await client.get_count("") == 0


@pytest.mark.asyncio
async def test_documents(client: EdinetClient) -> None:
    count = await client.get_count("2025-09-04")
    df = await client.get_entries("2025-09-04")
    assert df.shape == (count, 30)
    assert df.columns[0] == "Date"
    assert df["Date"].dtype == pl.Date


@pytest.mark.asyncio
async def test_documents_zero(client: EdinetClient) -> None:
    df = await client.get_entries("1000-01-01")
    assert df.shape == (0, 0)


@pytest.mark.asyncio
async def test_documents_holiday(client: EdinetClient) -> None:
    df = await client.get_entries("2025-09-23")
    assert df.shape == (0, 0)


@pytest.mark.asyncio
async def test_pdf(client: EdinetClient) -> None:
    df = await client.get_pdf("S100WKHJ")
    content = df.item(0, "pdf")
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
    assert df.columns[0] == "docID"
    assert df.shape == (47, 10)
    assert "値" in df.columns


@pytest_asyncio.fixture(scope="module")
async def df():
    client = EdinetClient()
    yield await client.get_entries("2025-06-27")
    await client.aclose()


def test_df_shape(df: DataFrame) -> None:
    assert df.shape == (1757, 30)


def test_df_xbrl_csv(df: DataFrame) -> None:
    df = df.filter(xbrlFlag="1")
    assert df.height == df.filter(csvFlag="1").height


def test_df_xbrl_pdf(df: DataFrame) -> None:
    df = df.filter(xbrlFlag="1")
    assert df.height == df.filter(pdfFlag="1").height
