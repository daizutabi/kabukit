from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest
from httpx import HTTPStatusError, Response

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
    expected_response = Response(200, json=json)
    post.return_value = expected_response
    expected_response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    response = await client.post("test/path", json={"key": "value"})

    assert response == json
    post.assert_awaited_once_with("test/path", json={"key": "value"})
    expected_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_post_failure(post: AsyncMock, mocker: MockerFixture) -> None:
    error_response = Response(400)
    post.return_value = error_response
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
async def test_get_success(get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"message": "success"}
    expected_response = Response(200, json=json)
    get.return_value = expected_response
    expected_response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    response = await client.get("test/path", params={"a": "b"})

    assert response == json
    get.assert_awaited_once_with("test/path", params={"a": "b"})
    expected_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_failure(get: AsyncMock, mocker: MockerFixture) -> None:
    error_response = Response(400)
    get.return_value = error_response
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
async def test_auth_success(post: AsyncMock, mocker: MockerFixture) -> None:
    from kabukit.utils.config import get_dotenv_path

    json = {"refreshToken": "refresh", "idToken": "id"}
    response = Response(200, json=json)
    post.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    await client.auth("", "", save=True)
    text = get_dotenv_path().read_text()
    assert "JQUANTS_REFRESH_TOKEN='refresh'\n" in text
    assert "JQUANTS_ID_TOKEN='id'\n" in text


@pytest.mark.asyncio
async def test_get_info(get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"info": [{"Date": "2023-01-01", "Code": "7203"}]}
    response = Response(200, json=json)
    get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_info(clean=False)
    assert df["Date"].to_list() == ["2023-01-01"]
    assert df["Code"].to_list() == ["7203"]


@pytest.mark.asyncio
async def test_iter_pages(get: AsyncMock, mocker: MockerFixture) -> None:
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

    get.side_effect = side_effect

    client = JQuantsClient("test_token")
    dfs = [df async for df in client.iter_pages("/test", {}, "info")]
    assert dfs[0]["Code"].to_list() == ["1", "2"]
    assert dfs[1]["Code"].to_list() == ["3", "4"]


@pytest.mark.asyncio
async def test_prices(get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"daily_quotes": [{"Open": 100}, {"Open": 200}]}
    response = Response(200, json=json)
    get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_prices("123", clean=False)
    assert df["Open"].to_list() == [100, 200]
    df = await client.get_latest_available_prices(clean=False)
    assert df["Open"].to_list() == [100, 200]
    df = await client.get_prices(clean=False)
    assert df["Open"].to_list() == [100, 200]


@pytest.mark.asyncio
async def test_prices_empty(get: AsyncMock, mocker: MockerFixture) -> None:
    json: dict[str, list[dict[str, str]]] = {"daily_quotes": []}
    response = Response(200, json=json)
    get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_prices("123")
    assert df.is_empty()
    df = await client.get_latest_available_prices()
    assert df.is_empty()


@pytest.mark.asyncio
async def test_prices_error(client: JQuantsClient) -> None:
    with pytest.raises(ValueError, match="dateとfrom/toの"):
        await client.get_prices(code="7203", date="2025-08-18", to="2025-08-16")


@pytest.mark.asyncio
async def test_statements(get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"statements": [{"Profit": 100}, {"Profit": 200}]}
    response = Response(200, json=json)
    get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_statements("123", clean=False)
    assert df["Profit"].to_list() == [100, 200]


@pytest.mark.asyncio
async def test_statements_empty(get: AsyncMock, mocker: MockerFixture) -> None:
    json: dict[str, list[dict[str, str]]] = {"statements": []}
    response = Response(200, json=json)
    get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_statements("123")
    assert df.is_empty()


@pytest.mark.asyncio
async def test_statements_error(client: JQuantsClient) -> None:
    with pytest.raises(ValueError, match="codeまたはdate"):
        await client.get_statements()


@pytest.mark.asyncio
async def test_announcement(get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"announcement": [{"Date": "2025-01-01"}]}
    response = Response(200, json=json)
    get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_announcement()
    assert df["Date"].to_list() == [datetime.date(2025, 1, 1)]


@pytest.mark.asyncio
async def test_announcement_empty(get: AsyncMock, mocker: MockerFixture) -> None:
    json: dict[str, list[dict[str, str]]] = {"announcement": []}
    response = Response(200, json=json)
    get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_announcement()
    assert df.is_empty()


@pytest.mark.asyncio
async def test_trades_spec(get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"trades_spec": [{"Date": "2025-01-01"}]}
    response = Response(200, json=json)
    get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_trades_spec()
    assert df["Date"].to_list() == [datetime.date(2025, 1, 1)]


@pytest.mark.asyncio
async def test_trades_spec_empty(get: AsyncMock, mocker: MockerFixture) -> None:
    json: dict[str, list[dict[str, str]]] = {"trades_spec": []}
    response = Response(200, json=json)
    get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_trades_spec()
    assert df.is_empty()
