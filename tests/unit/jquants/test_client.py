from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from unittest.mock import call

import pytest
from httpx import HTTPStatusError, Response
from polars import DataFrame

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
async def test_auth_successful_no_save(post: AsyncMock, mocker: MockerFixture) -> None:
    """Test successful authentication without saving tokens."""
    responses = [
        Response(200, json={"refreshToken": "test_refresh_token"}),
        Response(200, json={"idToken": "test_id_token"}),
    ]
    for r in responses:
        r.raise_for_status = mocker.MagicMock()
    post.side_effect = responses

    mock_set_key = mocker.patch("kabukit.jquants.client.set_key")

    client = JQuantsClient()
    await client.auth("test@example.com", "password", save=False)

    assert post.call_count == 2
    post.assert_any_call(
        "/token/auth_user",
        json={"mailaddress": "test@example.com", "password": "password"},
    )
    post.assert_any_call(
        "/token/auth_refresh?refreshtoken=test_refresh_token",
        json=None,
    )
    mock_set_key.assert_not_called()


@pytest.mark.asyncio
async def test_auth_successful_with_save(
    post: AsyncMock,
    mocker: MockerFixture,
) -> None:
    """Test successful authentication with saving tokens."""
    responses = [
        Response(200, json={"refreshToken": "test_refresh_token"}),
        Response(200, json={"idToken": "test_id_token"}),
    ]
    for r in responses:
        r.raise_for_status = mocker.MagicMock()
    post.side_effect = responses

    mock_set_key = mocker.patch("kabukit.jquants.client.set_key")

    client = JQuantsClient()
    await client.auth("test@example.com", "password", save=True)

    assert post.call_count == 2
    mock_set_key.assert_has_calls(
        [
            call(AuthKey.REFRESH_TOKEN, "test_refresh_token"),
            call(AuthKey.ID_TOKEN, "test_id_token"),
        ],
        any_order=True,
    )


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
@pytest.mark.parametrize(
    ("clean_flag", "with_date_flag", "clean_called", "with_date_called"),
    [
        (True, True, True, True),
        (True, False, True, False),
        (False, True, False, False),
        (False, False, False, False),
    ],
)
async def test_get_statements_flags(
    get: AsyncMock,
    mocker: MockerFixture,
    clean_flag: bool,
    with_date_flag: bool,
    clean_called: bool,
    with_date_called: bool,
) -> None:
    """Test the clean and with_date flags in get_statements."""
    # 1. Mock the API response
    json = {"statements": [{"LocalCode": "7203"}]}
    response = Response(200, json=json)
    get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    mock_clean = mocker.patch(
        "kabukit.jquants.statements.clean",
        return_value=DataFrame({"Code": ["7203"]}),
    )
    mock_with_date = mocker.patch(
        "kabukit.jquants.statements.with_date",
        return_value=DataFrame({"Date": [datetime.date(2023, 1, 1)]}),
    )

    client = JQuantsClient("test_token")
    await client.get_statements(
        code="7203",
        clean=clean_flag,
        with_date=with_date_flag,
    )

    if clean_called:
        mock_clean.assert_called_once()
    else:
        mock_clean.assert_not_called()

    if with_date_called:
        mock_with_date.assert_called_once()
    else:
        mock_with_date.assert_not_called()


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
