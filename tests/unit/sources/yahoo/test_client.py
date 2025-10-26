from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx import HTTPStatusError, Response

from kabukit.sources.yahoo.client import YahooClient

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_success(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    expected_response = Response(200, text="abc")
    mock_get.return_value = expected_response
    expected_response.raise_for_status = mocker.MagicMock()

    client = YahooClient()
    response = await client.get("test/path")

    assert response.text == "abc"
    mock_get.assert_awaited_once_with("test/path")
    expected_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_failure(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    error_response = Response(400)
    mock_get.return_value = error_response
    error_response.raise_for_status = mocker.MagicMock(
        side_effect=HTTPStatusError(
            "Bad Request",
            request=mocker.MagicMock(),
            response=error_response,
        ),
    )

    client = YahooClient()

    with pytest.raises(HTTPStatusError):
        await client.get("test/path")

    error_response.raise_for_status.assert_called_once()


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
