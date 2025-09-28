import pytest_asyncio

from kabukit.jquants.client import JQuantsClient


@pytest_asyncio.fixture
async def jquants_client():
    async with JQuantsClient() as client:
        yield client
