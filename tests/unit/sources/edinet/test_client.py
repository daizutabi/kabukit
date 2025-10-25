from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx import HTTPStatusError, Response

from kabukit.sources.edinet.client import AuthKey, EdinetClient

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


def test_set_api_key() -> None:
    client = EdinetClient("abc")
    assert client.client.params["Subscription-Key"] == "abc"


def test_set_api_key_none_and_no_config(mocker: MockerFixture) -> None:
    mock_get_config_value = mocker.patch(
        "kabukit.sources.edinet.client.get_config_value",
        return_value=None,
    )
    client = EdinetClient()
    assert "Subscription-Key" not in client.client.params
    mock_get_config_value.assert_called_once_with(AuthKey.API_KEY)


def test_set_api_key_directly(mocker: MockerFixture) -> None:
    mock_get_config_value = mocker.patch(
        "kabukit.sources.edinet.client.get_config_value",
        return_value="should_not_be_called",
    )
    client = EdinetClient("initial_key")
    client.set_api_key("new_key")
    assert client.client.params["Subscription-Key"] == "new_key"
    mock_get_config_value.assert_not_called()


@pytest.mark.asyncio
async def test_get_success(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    expected_response = Response(200, json={"message": "success"})
    mock_get.return_value = expected_response
    expected_response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    response = await client.get("test/path", params={"a": "b"})

    assert response == expected_response
    mock_get.assert_awaited_once_with("test/path", params={"a": "b"})
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

    client = EdinetClient("test_key")

    with pytest.raises(HTTPStatusError):
        await client.get("test/path", params={})

    error_response.raise_for_status.assert_called_once()
