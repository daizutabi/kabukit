from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest

from kabukit.jquants.client import AuthKey, JQuantsClient

if TYPE_CHECKING:
    from unittest.mock import AsyncMock, MagicMock

    from pytest_mock import MockerFixture


def test_set_id_token() -> None:
    client = JQuantsClient("abc")
    assert client.client.headers["Authorization"] == "Bearer abc"


def test_set_id_token_none(mocker: MockerFixture) -> None:
    mocker.patch.dict("os.environ", {AuthKey.ID_TOKEN: "def"})
    client = JQuantsClient()
    assert client.client.headers["Authorization"] == "Bearer def"


@pytest.fixture
def async_client(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.core.client.AsyncClient").return_value


@pytest.fixture
def post(async_client: MagicMock, mocker: MockerFixture) -> AsyncMock:
    post = mocker.AsyncMock()
    async_client.post = post
    return post


@pytest.fixture
def get(async_client: MagicMock, mocker: MockerFixture) -> AsyncMock:
    get = mocker.AsyncMock()
    async_client.get = get
    return get


@pytest.mark.asyncio
async def test_post_success(post: AsyncMock, mocker: MockerFixture) -> None:
    json = {"message": "success"}
    expected_response = httpx.Response(200, json=json)
    post.return_value = expected_response
    expected_response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    response = await client.post("test/path", json={"key": "value"})

    assert response == json
    post.assert_awaited_once_with("test/path", json={"key": "value"})
    expected_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_post_failure(post: AsyncMock, mocker: MockerFixture) -> None:
    error_response = httpx.Response(400)
    post.return_value = error_response
    error_response.raise_for_status = mocker.MagicMock(
        side_effect=httpx.HTTPStatusError(
            "Bad Request",
            request=mocker.MagicMock(),
            response=error_response,
        ),
    )

    client = JQuantsClient("test_token")

    with pytest.raises(httpx.HTTPStatusError):
        await client.post("test/path")

    error_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_success(get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"message": "success"}
    expected_response = httpx.Response(200, json=json)
    get.return_value = expected_response
    expected_response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    response = await client.get("test/path", params={"a": "b"})

    assert response == json
    get.assert_awaited_once_with("test/path", params={"a": "b"})
    expected_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_failure(get: AsyncMock, mocker: MockerFixture) -> None:
    error_response = httpx.Response(400)
    get.return_value = error_response
    error_response.raise_for_status = mocker.MagicMock(
        side_effect=httpx.HTTPStatusError(
            "Bad Request",
            request=mocker.MagicMock(),
            response=error_response,
        ),
    )

    client = JQuantsClient("test_token")

    with pytest.raises(httpx.HTTPStatusError):
        await client.get("test/path")

    error_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_auth_success(post: AsyncMock, mocker: MockerFixture) -> None:
    from kabukit.utils.config import get_dotenv_path

    json = {"refreshToken": "refresh", "idToken": "id"}
    respose = httpx.Response(200, json=json)
    post.return_value = respose
    respose.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    await client.auth("", "", save=True)
    text = get_dotenv_path().read_text()
    assert "JQUANTS_REFRESH_TOKEN='refresh'\n" in text
    assert "JQUANTS_ID_TOKEN='id'\n" in text


@pytest.mark.asyncio
async def test_get_info(get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"info": [{"Date": "2023-01-01", "Code": "7203"}]}
    respose = httpx.Response(200, json=json)
    get.return_value = respose
    respose.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_info(clean=False)
    assert df["Date"].to_list() == ["2023-01-01"]
    assert df["Code"].to_list() == ["7203"]
