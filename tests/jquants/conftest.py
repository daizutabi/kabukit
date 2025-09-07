import pytest_asyncio

from kabukit.jquants.client import JQuantsClient


@pytest_asyncio.fixture
async def client():
    client = JQuantsClient()
    yield client
    await client.aclose()
