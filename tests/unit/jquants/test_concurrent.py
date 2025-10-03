from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import expectedFailure

import pytest
from polars import DataFrame

from kabukit.jquants.client import JQuantsClient

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture


def dummy_progress(x: Iterable[Any]) -> Iterable[Any]:
    return x


def dummy_callback(df: DataFrame) -> DataFrame:
    return df


@pytest.fixture
def mock_util_fetch(mocker: MockerFixture) -> AsyncMock:
    """kabukit.utils.concurrent.fetch のモック"""
    return mocker.patch(
        "kabukit.utils.concurrent.fetch",
        new_callable=mocker.AsyncMock,
    )


@pytest.fixture
def mock_get_codes(mocker: MockerFixture) -> AsyncMock:
    """kabukit.jquants.info.get_codes のモック"""
    return mocker.patch(
        "kabukit.jquants.concurrent.get_codes",
        new_callable=mocker.AsyncMock,
    )


@pytest.mark.asyncio
async def test_fetch(mock_util_fetch: AsyncMock) -> None:
    from kabukit.jquants.concurrent import fetch

    mock_util_fetch.return_value = DataFrame(
        {"Date": [4, 3, 2, 1], "Code": ["a", "b", "b", "a"]},
    )

    result = await fetch(
        "test_resource",
        ["1234", "5678"],
        max_concurrency=10,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    expected = DataFrame({"Date": [1, 4, 2, 3], "Code": ["a", "a", "b", "b"]})
    assert result.equals(expected)

    mock_util_fetch.assert_awaited_once_with(
        JQuantsClient,
        "test_resource",
        ["1234", "5678"],
        max_concurrency=10,
        progress=dummy_progress,
        callback=dummy_callback,
    )


@pytest.mark.asyncio
async def test_fetch_all(mocker: MockerFixture, mock_get_codes: AsyncMock) -> None:
    from kabukit.jquants.concurrent import fetch_all

    mock_get_codes.return_value = ["1111", "2222", "3333"]
    mock_fetch = mocker.patch(
        "kabukit.jquants.concurrent.fetch",
        new_callable=mocker.AsyncMock,
    )
    mock_fetch.return_value = DataFrame({"b": [2]})

    result = await fetch_all(
        "test_resource",
        limit=2,
        max_concurrency=5,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    assert result.equals(DataFrame({"b": [2]}))
    mock_get_codes.assert_awaited_once()
    mock_fetch.assert_awaited_once_with(
        "test_resource",
        ["1111", "2222"],
        max_concurrency=5,
        progress=dummy_progress,
        callback=dummy_callback,
    )
