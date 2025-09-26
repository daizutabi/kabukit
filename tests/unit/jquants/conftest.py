import pytest_asyncio

from kabukit.jquants.client import JQuantsClient


@pytest_asyncio.fixture
async def client():
    async with JQuantsClient("test_token") as client:
        yield client
