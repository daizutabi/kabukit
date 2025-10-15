from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx import HTTPStatusError, Response

from kabukit.jquants.client import AuthKey, JQuantsClient

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


def test_set_id_token() -> None:
    client = JQuantsClient("abc")
    assert client.client.headers["Authorization"] == "Bearer abc"


def test_set_id_token_none(mocker: MockerFixture) -> None:
    mock_get_config_value = mocker.patch(
        "kabukit.jquants.client.get_config_value",
        return_value="def",
    )
    client = JQuantsClient()
    assert client.client.headers["Authorization"] == "Bearer def"
    mock_get_config_value.assert_called_once_with(AuthKey.ID_TOKEN)


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_get_success(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"message": "success"}
    expected_response = Response(200, json=json)
    mock_get.return_value = expected_response
    expected_response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    response = await client.get("test/path", params={"a": "b"})

    assert response == json
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

    client = JQuantsClient("test_token")

    with pytest.raises(HTTPStatusError):
        await client.get("test/path")

    error_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_auth_returns_token(
    mock_post: AsyncMock,
    mocker: MockerFixture,
) -> None:
    """Test successful authentication returns token."""
    responses = [
        Response(200, json={"refreshToken": "test_refresh_token"}),
        Response(200, json={"idToken": "test_id_token"}),
    ]
    for r in responses:
        r.raise_for_status = mocker.MagicMock()
    mock_post.side_effect = responses

    client = JQuantsClient()
    client.client.headers = {}
    token = await client.auth("test@example.com", "password")

    assert token == "test_id_token"
    assert client.client.headers["Authorization"] == "Bearer test_id_token"


@pytest.mark.asyncio
async def test_auth_value_error_missing_mailaddress(mocker: MockerFixture) -> None:
    def side_effect(key: str) -> str | None:
        if key == AuthKey.PASSWORD:
            return "config_pass"
        return None

    mocker.patch("kabukit.jquants.client.get_config_value", side_effect=side_effect)
    client = JQuantsClient()

    with pytest.raises(ValueError, match="メールアドレスとパスワードを指定するか"):
        await client.auth(password="test_pass")  # noqa: S106


@pytest.mark.asyncio
async def test_auth_value_error_missing_password(mocker: MockerFixture) -> None:
    def side_effect(key: str) -> str | None:
        if key == AuthKey.MAILADDRESS:
            return "config@example.com"
        return None

    mocker.patch("kabukit.jquants.client.get_config_value", side_effect=side_effect)
    client = JQuantsClient()

    with pytest.raises(ValueError, match="メールアドレスとパスワードを指定するか"):
        await client.auth(mailaddress="test@example.com")


@pytest.mark.asyncio
async def test_auth_success_with_config_mailaddress(
    mock_post: AsyncMock,
    mocker: MockerFixture,
) -> None:
    def side_effect(key: str) -> str | None:
        if key == AuthKey.MAILADDRESS:
            return "config@example.com"
        return "config_pass"

    mocker.patch("kabukit.jquants.client.get_config_value", side_effect=side_effect)
    responses = [
        Response(200, json={"refreshToken": "test_refresh_token"}),
        Response(200, json={"idToken": "test_id_token"}),
    ]
    for r in responses:
        r.raise_for_status = mocker.MagicMock()
    mock_post.side_effect = responses

    client = JQuantsClient()
    token = await client.auth(password="test_pass")  # noqa: S106

    assert token == "test_id_token"
    mock_post.assert_any_call(
        "/token/auth_user",
        json={"mailaddress": "config@example.com", "password": "test_pass"},
    )


@pytest.mark.asyncio
async def test_auth_success_with_config_password(
    mock_post: AsyncMock,
    mocker: MockerFixture,
) -> None:
    def side_effect(key: str) -> str | None:
        if key == AuthKey.MAILADDRESS:
            return "config@example.com"
        return "config_pass"

    mocker.patch("kabukit.jquants.client.get_config_value", side_effect=side_effect)
    responses = [
        Response(200, json={"refreshToken": "test_refresh_token"}),
        Response(200, json={"idToken": "test_id_token"}),
    ]
    for r in responses:
        r.raise_for_status = mocker.MagicMock()
    mock_post.side_effect = responses

    client = JQuantsClient()
    token = await client.auth(mailaddress="test@example.com")  # password is None

    assert token == "test_id_token"
    mock_post.assert_any_call(
        "/token/auth_user",
        json={"mailaddress": "test@example.com", "password": "config_pass"},
    )


@pytest.mark.asyncio
async def test_auth_http_status_error_auth_user(
    mock_post: AsyncMock,
    mocker: MockerFixture,
) -> None:
    """Test HTTPStatusError during auth_user POST."""
    error_response = Response(401)
    error_response.raise_for_status = mocker.MagicMock(
        side_effect=HTTPStatusError(
            "Unauthorized",
            request=mocker.MagicMock(),
            response=error_response,
        ),
    )
    mock_post.side_effect = [error_response]

    client = JQuantsClient()
    with pytest.raises(HTTPStatusError):
        await client.auth("test@example.com", "password")


@pytest.mark.asyncio
async def test_auth_http_status_error_auth_refresh(
    mock_post: AsyncMock,
    mocker: MockerFixture,
) -> None:
    """Test HTTPStatusError during auth_refresh POST."""
    success_response = Response(200, json={"refreshToken": "test_refresh_token"})
    success_response.raise_for_status = mocker.MagicMock()

    error_response = Response(401)
    error_response.raise_for_status = mocker.MagicMock(
        side_effect=HTTPStatusError(
            "Unauthorized",
            request=mocker.MagicMock(),
            response=error_response,
        ),
    )
    mock_post.side_effect = [success_response, error_response]

    client = JQuantsClient()
    with pytest.raises(HTTPStatusError):
        await client.auth("test@example.com", "password")


@pytest.mark.asyncio
async def test_auth_set_id_token_called(
    mock_post: AsyncMock,
    mocker: MockerFixture,
) -> None:
    """Test that set_id_token is called with the obtained ID token."""
    responses = [
        Response(200, json={"refreshToken": "test_refresh_token"}),
        Response(200, json={"idToken": "expected_id_token"}),
    ]
    for r in responses:
        r.raise_for_status = mocker.MagicMock()
    mock_post.side_effect = responses

    client = JQuantsClient()
    # Spy on the set_id_token method
    set_id_token_spy = mocker.spy(client, "set_id_token")
    await client.auth("test@example.com", "password")

    set_id_token_spy.assert_called_once_with("expected_id_token")


@pytest.mark.asyncio
async def test_iter_pages(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    def side_effect(_url: str, params: dict[str, str]) -> Response:
        if "pagination_key" not in params:
            response = Response(
                200,
                json={
                    "info": [{"Code": "1"}, {"Code": "2"}],
                    "pagination_key": "2",
                },
            )
        else:
            response = Response(
                200,
                json={"info": [{"Code": "3"}, {"Code": "4"}]},
            )
        response.raise_for_status = mocker.MagicMock()
        return response

    mock_get.side_effect = side_effect

    client = JQuantsClient("test_token")
    dfs = [df async for df in client.iter_pages("/test", {}, "info")]
    assert dfs[0]["Code"].to_list() == ["1", "2"]
    assert dfs[1]["Code"].to_list() == ["3", "4"]
