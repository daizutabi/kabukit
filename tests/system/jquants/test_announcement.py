import pytest

from kabukit.jquants.client import JQuantsClient

pytestmark = pytest.mark.system


@pytest.mark.asyncio
async def test_get(client: JQuantsClient) -> None:
    df = await client.get_announcement()
    assert df.width in [7, 0]
