from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest
from polars import DataFrame

from kabukit.edinet.client import EdinetClient

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any
    from unittest.mock import AsyncMock, MagicMock

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


@pytest.mark.asyncio
async def test_fetch(mock_util_fetch: AsyncMock) -> None:
    from kabukit.edinet.concurrent import fetch

    mock_util_fetch.return_value = DataFrame({"a": [1]})

    result = await fetch(
        "test_resource",
        ["arg1", "arg2"],
        max_concurrency=10,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    assert result.equals(DataFrame({"a": [1]}))
    mock_util_fetch.assert_awaited_once_with(
        EdinetClient,
        "test_resource",
        ["arg1", "arg2"],
        max_concurrency=10,
        progress=dummy_progress,
        callback=dummy_callback,
    )


@pytest.fixture
def mock_get_dates(mocker: MockerFixture) -> MagicMock:
    """kabukit.edinet.concurrent.get_dates のモック"""
    return mocker.patch("kabukit.edinet.concurrent.get_dates")


@pytest.mark.asyncio
async def test_fetch_list(mocker: MockerFixture, mock_get_dates: MagicMock) -> None:
    from kabukit.edinet.concurrent import fetch_list

    mock_get_dates.return_value = [
        datetime.date(2023, 1, 3),
        datetime.date(2023, 1, 2),
        datetime.date(2023, 1, 1),
    ]
    mock_fetch = mocker.patch(
        "kabukit.edinet.concurrent.fetch",
        new_callable=mocker.AsyncMock,
    )
    mock_fetch.return_value = DataFrame({"Date": [2]})

    result = await fetch_list(
        days=3,
        limit=2,
        max_concurrency=5,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    assert result.equals(DataFrame({"Date": [2]}))
    mock_get_dates.assert_called_once_with(days=3, years=None)
    mock_fetch.assert_awaited_once_with(
        "list",
        [datetime.date(2023, 1, 3), datetime.date(2023, 1, 2)],
        max_concurrency=5,
        progress=dummy_progress,
        callback=dummy_callback,
    )


@pytest.mark.asyncio
async def test_fetch_csv(mocker: MockerFixture) -> None:
    from kabukit.edinet.concurrent import fetch_csv

    mock_fetch = mocker.patch(
        "kabukit.edinet.concurrent.fetch",
        new_callable=mocker.AsyncMock,
    )
    mock_fetch.return_value = DataFrame({"docID": [3]})

    result = await fetch_csv(
        ["doc1", "doc2", "doc3"],
        limit=2,
        max_concurrency=5,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    assert result.equals(DataFrame({"docID": [3]}))
    mock_fetch.assert_awaited_once_with(
        "csv",
        ["doc1", "doc2"],
        max_concurrency=5,
        progress=dummy_progress,
        callback=dummy_callback,
    )
