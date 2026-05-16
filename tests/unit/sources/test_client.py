from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, ClassVar

import pytest
from httpx import ConnectTimeout, HTTPStatusError, Response

from kabukit.sources.client import Client

if TYPE_CHECKING:
    from collections.abc import Callable
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


class MockClient(Client):
    base_url: ClassVar[str] = "http://mock.api"


async def test_async_with() -> None:
    async with MockClient() as client:
        assert not client.client.is_closed

    assert client.client.is_closed


async def test_get_success(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    expected_response = Response(200, json={"message": "success"})
    mock_get.return_value = expected_response
    expected_response.raise_for_status = mocker.MagicMock()

    client = MockClient()
    response = await client.get("test/path", params={"a": "b"})

    assert response == expected_response
    mock_get.assert_awaited_once_with("test/path", params={"a": "b"})
    expected_response.raise_for_status.assert_called_once()


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

    client = MockClient()

    with pytest.raises(HTTPStatusError):
        await client.get("test/path", params={})

    error_response.raise_for_status.assert_called_once()


async def test_get_retries_on_failure(
    mock_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    """Test that the get method retries on retryable failures."""
    mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)
    error = ConnectTimeout("Connection timed out")
    success_response = Response(200, json={"message": "success"})
    success_response.raise_for_status = mocker.MagicMock()

    mock_get.side_effect = [error, error, success_response]

    client = MockClient()
    response = await client.get("test/path", params={})

    assert response == success_response
    assert mock_get.call_count == 3
    assert mock_sleep.call_count == 2


async def test_get_fails_after_retries(
    mock_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    """Test that the get method fails after exhausting all retries."""
    mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)
    error = ConnectTimeout("Connection timed out")
    mock_get.side_effect = [error, error, error]

    client = MockClient()

    with pytest.raises(ConnectTimeout):
        await client.get("test/path", params={})

    assert mock_get.call_count == 3
    assert mock_sleep.call_count == 2


async def test_run_in_executor_without_executor(mocker: MockerFixture) -> None:
    mock_loop = mocker.MagicMock()
    mock_loop.run_in_executor = mocker.AsyncMock()
    mocker.patch(
        "kabukit.sources.client.asyncio.get_running_loop",
        return_value=mock_loop,
    )

    client = MockClient(executor=None)

    result = await client.run_in_executor(sum, [1, 2, 3])
    assert result == 6

    mock_loop.run_in_executor.assert_not_called()


def side_effect[T](_executor: Any, func_to_run: Callable[[], T]):  # pyright: ignore[reportUnknownParameterType]
    future = asyncio.Future()  # pyright: ignore[reportUnknownVariableType]
    future.set_result(func_to_run())  # pyright: ignore[reportUnknownMemberType]
    return future  # pyright: ignore[reportUnknownVariableType]


async def test_run_in_executor_with_executor(mocker: MockerFixture) -> None:
    mock_loop = mocker.MagicMock()
    mock_loop.run_in_executor.side_effect = side_effect
    mocker.patch(
        "kabukit.sources.client.asyncio.get_running_loop",
        return_value=mock_loop,
    )

    mock_executor = mocker.MagicMock()
    client = MockClient(executor=mock_executor)

    result = await client.run_in_executor(sum, [1, 2, 3])

    assert result == 6  # 戻り値を検証
    mock_loop.run_in_executor.assert_called_once_with(mock_executor, mocker.ANY)


async def test_run_in_executor_with_executor_and_kwargs(mocker: MockerFixture) -> None:
    mock_loop = mocker.MagicMock()
    mock_loop.run_in_executor.side_effect = side_effect
    mocker.patch(
        "kabukit.sources.client.asyncio.get_running_loop",
        return_value=mock_loop,
    )

    mock_executor = mocker.MagicMock()
    client = MockClient(executor=mock_executor)

    def dummy_func(a: int, b: int = 0, c: int = 0) -> int:
        return a + b + c

    result = await client.run_in_executor(dummy_func, 1, b=2, c=3)

    assert result == 6  # キーワード引数を含めた結果を検証
    mock_loop.run_in_executor.assert_called_once_with(mock_executor, mocker.ANY)
