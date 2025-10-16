import pytest_asyncio

from kabukit.edinet.client import AuthKey as EdinetAuthKey
from kabukit.utils.config import get_config_value


@pytest_asyncio.fixture
async def client():
    from kabukit.edinet.client import EdinetClient

    # デバッグ用: APIキーが正しく取得されているか確認
    key = get_config_value(EdinetAuthKey.API_KEY)
    assert key
    print(f"\n[DEBUG] API Key from config/env: {key[:10]}")  # noqa: T201

    async with EdinetClient() as client:
        key = client.client.params.get("Subscription-Key")
        assert key
        print(f"[DEBUG] EdinetClient Subscription-Key: {key[:10]}")  # noqa: T201
        yield client
