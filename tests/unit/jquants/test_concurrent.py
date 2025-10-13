from __future__ import annotations

from typing import TYPE_CHECKING

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
def mock_utils_get(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.utils.concurrent.get",
        new_callable=mocker.AsyncMock,
    )


@pytest.fixture
def mock_get_target_codes(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.jquants.concurrent.get_target_codes",
        new_callable=mocker.AsyncMock,
    )


@pytest.mark.asyncio
async def test_get(mock_utils_get: AsyncMock) -> None:
    from kabukit.jquants.concurrent import get

    mock_utils_get.return_value = DataFrame(
        {"Date": [4, 3, 2, 1], "Code": ["a", "b", "b", "a"]},
    )

    result = await get(
        "test_resource",
        ["1234", "5678"],
        max_concurrency=10,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    expected = DataFrame({"Date": [1, 4, 2, 3], "Code": ["a", "a", "b", "b"]})
    assert result.equals(expected)

    mock_utils_get.assert_awaited_once_with(
        JQuantsClient,
        "test_resource",
        ["1234", "5678"],
        limit=None,
        max_concurrency=10,
        progress=dummy_progress,
        callback=dummy_callback,
    )


@pytest.mark.asyncio
async def test_get_without_codes(
    mock_utils_get: AsyncMock,
    mock_get_target_codes: AsyncMock,
) -> None:
    from kabukit.jquants.concurrent import get

    mock_get_target_codes.return_value = ["1111", "2222", "3333"]
    # get() は .sort("Code", "Date") を行うので、モックの戻り値にもカラムが必要
    mock_utils_get.return_value = DataFrame(
        {"Date": [1], "Code": ["c"], "b": [2]},
    )

    result = await get(
        "test_resource",
        None,  # codes=None を明示的に渡す
        limit=2,
        max_concurrency=5,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    # ソート後の結果を期待値とする
    expected = DataFrame({"Date": [1], "Code": ["c"], "b": [2]})
    assert result.equals(expected)

    mock_get_target_codes.assert_awaited_once()
    mock_utils_get.assert_awaited_once_with(
        JQuantsClient,
        "test_resource",
        ["1111", "2222", "3333"],  # get_target_codes の結果が渡される
        limit=2,
        max_concurrency=5,
        progress=dummy_progress,
        callback=dummy_callback,
    )
