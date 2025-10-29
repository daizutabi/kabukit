from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx import HTTPStatusError, Response

from kabukit.sources.jquants.client import AuthKey, JQuantsClient

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


def test_set_id_token() -> None:
    client = JQuantsClient("abc")
    assert client.client.headers["Authorization"] == "Bearer abc"


def test_set_id_token_none(mocker: MockerFixture) -> None:
    mock_get_config_value = mocker.patch(
        "kabukit.sources.jquants.client.get_config_value",
        return_value="def",
    )
    client = JQuantsClient()
    assert client.client.headers["Authorization"] == "Bearer def"
    mock_get_config_value.assert_called_once_with(AuthKey.ID_TOKEN)


async def test_post_success(mock_post: AsyncMock, mocker: MockerFixture) -> None:
    json = {"message": "success"}
    expected_response = Response(200, json=json)
    mock_post.return_value = expected_response
    expected_response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    response = await client.post("test/path", json={"key": "value"})

    assert response == json
    mock_post.assert_awaited_once_with("test/path", json={"key": "value"})
    expected_response.raise_for_status.assert_called_once()


async def test_post_failure(mock_post: AsyncMock, mocker: MockerFixture) -> None:
    error_response = Response(400)
    mock_post.return_value = error_response
    error_response.raise_for_status = mocker.MagicMock(
        side_effect=HTTPStatusError(
            "Bad Request",
            request=mocker.MagicMock(),
            response=error_response,
        ),
    )

    client = JQuantsClient("test_token")

    with pytest.raises(HTTPStatusError):
        await client.post("test/path")

    error_response.raise_for_status.assert_called_once()
