import pytest_asyncio


@pytest_asyncio.fixture
async def client():
    from kabukit.edinet.client import EdinetClient

    async with EdinetClient() as client:
        yield client
