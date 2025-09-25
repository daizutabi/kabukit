import pytest_asyncio


@pytest_asyncio.fixture
async def client():
    from kabukit.edinet.client import EdinetClient

    client = EdinetClient()
    yield client
    await client.aclose()
