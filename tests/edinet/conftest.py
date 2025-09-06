import pytest_asyncio


@pytest_asyncio.fixture
async def client():
    from kabukit.edinet.client import EdinetClient

    client = EdinetClient.create()
    yield client
    await client.aclose()
