from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx import Response

from kabukit.sources.yahoo.client import YahooClient

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
@pytest.mark.parametrize("use_executor", [True, False])
async def test_get_quote(mocker: MockerFixture, *, use_executor: bool) -> None:
    text = """\
        <script>
            window.__PRELOADED_STATE__ = {"key": "value"};
        </script>
    """
    mock_get = mocker.patch.object(YahooClient, "get")
    mock_get.return_value = Response(200, text=text)

    client = YahooClient()
    df = await client.get_quote("2703", use_executor=use_executor)

    assert df["Code"].unique().to_list() == ["27030"]
    mock_get.assert_awaited_once_with("2703.T")
