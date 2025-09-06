import pytest
import pytest_asyncio

from kabukit.edinet.client import EdinetClient


@pytest_asyncio.fixture
async def client():
    client = EdinetClient.create()
    yield client
    await client.aclose()


@pytest.mark.asyncio
async def test_count(client: EdinetClient) -> None:
    assert await client.get_count("2025-09-05") > 0


@pytest.mark.asyncio
async def test_count_zero(client: EdinetClient) -> None:
    assert await client.get_count("1000-01-01") == 0


@pytest.mark.asyncio
async def test_list(client: EdinetClient) -> None:
    count = await client.get_count("2025-09-04")
    df = await client.get_list("2025-09-04")
    assert df.shape == (count, 29)


@pytest.mark.asyncio
async def test_list_zero(client: EdinetClient) -> None:
    df = await client.get_list("1000-01-01")
    assert df.shape == (0, 0)


@pytest.mark.asyncio
async def test_pdf(client: EdinetClient) -> None:
    assert await client.get_pdf("S100WKHJ")


@pytest.mark.asyncio
async def test_zip(client: EdinetClient) -> None:
    assert await client.get_zip("S100WKHJ", doc_type=5)
