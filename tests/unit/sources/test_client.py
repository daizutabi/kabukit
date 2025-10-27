from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx import ConnectTimeout, HTTPStatusError, Response

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_async_with() -> None:
    from kabukit.sources.client import Client

    async with Client() as client:
        assert not client.client.is_closed

    assert client.client.is_closed


@pytest.mark.asyncio
async def test_get_success(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    from kabukit.sources.client import Client

    expected_response = Response(200, json={"message": "success"})
    mock_get.return_value = expected_response
    expected_response.raise_for_status = mocker.MagicMock()

    client = Client("test_key")
    response = await client.get("test/path", params={"a": "b"})

    assert response == expected_response
    mock_get.assert_awaited_once_with("test/path", params={"a": "b"})
    expected_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_failure(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    from kabukit.sources.client import Client

    error_response = Response(400)
    mock_get.return_value = error_response
    error_response.raise_for_status = mocker.MagicMock(
        side_effect=HTTPStatusError(
            "Bad Request",
            request=mocker.MagicMock(),
            response=error_response,
        ),
    )

    client = Client("test_key")

    with pytest.raises(HTTPStatusError):
        await client.get("test/path", params={})

    error_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_retries_on_failure(
    mock_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    """Test that the get method retries on retryable failures."""
    from kabukit.sources.client import Client

    mock_sleep = mocker.patch("asyncio.sleep")
    error = ConnectTimeout("Connection timed out")
    success_response = Response(200, json={"message": "success"})
    success_response.raise_for_status = mocker.MagicMock()

    mock_get.side_effect = [error, error, success_response]

    client = Client("test_key")
    response = await client.get("test/path", params={})

    assert response == success_response
    assert mock_get.call_count == 3
    assert mock_sleep.call_count == 2


@pytest.mark.asyncio
async def test_get_fails_after_retries(
    mock_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    """Test that the get method fails after exhausting all retries."""
    from kabukit.sources.client import Client

    mock_sleep = mocker.patch("asyncio.sleep")
    error = ConnectTimeout("Connection timed out")
    mock_get.side_effect = [error, error, error]

    client = Client("test_key")

    with pytest.raises(ConnectTimeout):
        await client.get("test/path", params={})

    assert mock_get.call_count == 3
    assert mock_sleep.call_count == 2
