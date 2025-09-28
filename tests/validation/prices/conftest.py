import pytest_asyncio

from kabukit.jquants.client import JQuantsClient
from tests.validation.conftest import pytestmark  # noqa: F401


@pytest_asyncio.fixture
async def client():
    async with JQuantsClient() as client:
        yield client
