from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest
from polars import DataFrame

from kabukit.sources.edinet.client import EdinetClient

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any
    from unittest.mock import AsyncMock, MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


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


@pytest.mark.asyncio
async def test_get(mock_utils_get: AsyncMock) -> None:
    from kabukit.sources.edinet.concurrent import get

    mock_utils_get.return_value = DataFrame({"a": [1]})

    result = await get(
        "test_resource",
        ["arg1", "arg2"],
        max_concurrency=10,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    assert result.equals(DataFrame({"a": [1]}))
    mock_utils_get.assert_awaited_once_with(
        EdinetClient,
        "test_resource",
        ["arg1", "arg2"],
        max_items=None,
        max_concurrency=10,
        progress=dummy_progress,
        callback=dummy_callback,
    )


@pytest.fixture
def mock_get_dates(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.sources.edinet.concurrent.get_dates")


@pytest.mark.asyncio
async def test_get_entries_days(
    mocker: MockerFixture,
    mock_get_dates: MagicMock,
) -> None:
    from kabukit.sources.edinet.concurrent import get_entries

    mock_get_dates.return_value = [
        datetime.date(2023, 1, 3),
        datetime.date(2023, 1, 2),
        datetime.date(2023, 1, 1),
    ]
    mock_get = mocker.patch(
        "kabukit.sources.edinet.concurrent.get",
        new_callable=mocker.AsyncMock,
    )
    mock_get.return_value = DataFrame({"Date": [2], "Code": ["10000"]})

    result = await get_entries(
        days=3,
        max_items=2,
        max_concurrency=5,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    assert result.equals(DataFrame({"Date": [2], "Code": ["10000"]}))
    mock_get_dates.assert_called_once_with(days=3, years=None)
    mock_get.assert_awaited_once_with(
        "entries",
        [
            datetime.date(2023, 1, 3),
            datetime.date(2023, 1, 2),
            datetime.date(2023, 1, 1),
        ],
        max_items=2,
        max_concurrency=5,
        progress=dummy_progress,
        callback=dummy_callback,
    )


@pytest.mark.asyncio
async def test_get_entries_years(
    mocker: MockerFixture,
    mock_get_dates: MagicMock,
) -> None:
    from kabukit.sources.edinet.concurrent import get_entries

    mock_get_dates.return_value = [
        datetime.date(2023, 1, 1),
        datetime.date(2022, 1, 1),
    ]
    mock_get = mocker.patch(
        "kabukit.sources.edinet.concurrent.get",
        new_callable=mocker.AsyncMock,
    )
    mock_get.return_value = DataFrame({"Date": [1], "Code": ["10000"]})

    await get_entries(years=2)

    mock_get_dates.assert_called_once_with(days=None, years=2)
    mock_get.assert_awaited_once_with(
        "entries",
        [
            datetime.date(2023, 1, 1),
            datetime.date(2022, 1, 1),
        ],
        max_items=None,
        max_concurrency=None,
        progress=None,
        callback=None,
    )


@pytest.mark.asyncio
async def test_get_entries_single_date(mock_edinet_client_context: AsyncMock) -> None:
    from kabukit.sources.edinet.concurrent import get_entries

    target_date = datetime.date(2025, 10, 10)
    await get_entries(target_date)

    mock_edinet_client_context.get_entries.assert_awaited_once_with(target_date)


@pytest.mark.asyncio
async def test_get_entries_invalid_date(mocker: MockerFixture) -> None:
    from kabukit.sources.edinet.concurrent import get_entries

    mock_get = mocker.patch(
        "kabukit.sources.edinet.concurrent.get",
        new_callable=mocker.AsyncMock,
    )
    mock_get.return_value = DataFrame()

    result = await get_entries(["2025-10-10"])
    assert result.is_empty()


@pytest.mark.asyncio
async def test_get_documents_csv(mocker: MockerFixture) -> None:
    from kabukit.sources.edinet.concurrent import get_documents

    mock_get = mocker.patch(
        "kabukit.sources.edinet.concurrent.get",
        new_callable=mocker.AsyncMock,
    )
    mock_get.return_value = DataFrame({"docID": [3]})

    result = await get_documents(
        ["doc1", "doc2", "doc3"],
        max_items=2,
        max_concurrency=5,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    assert result.equals(DataFrame({"docID": [3]}))
    mock_get.assert_awaited_once_with(
        "csv",
        ["doc1", "doc2", "doc3"],
        max_items=2,
        max_concurrency=5,
        progress=dummy_progress,
        callback=dummy_callback,
    )


@pytest.mark.asyncio
async def test_get_documents_pdf(mocker: MockerFixture) -> None:
    from kabukit.sources.edinet.concurrent import get_documents

    mock_get = mocker.patch(
        "kabukit.sources.edinet.concurrent.get",
        new_callable=mocker.AsyncMock,
    )
    mock_get.return_value = DataFrame({"docID": [1]})

    await get_documents(["doc1", "doc2"], pdf=True)

    mock_get.assert_awaited_once_with(
        "pdf",
        ["doc1", "doc2"],
        max_items=None,
        max_concurrency=None,
        progress=None,
        callback=None,
    )


@pytest.mark.asyncio
async def test_get_documents_single_doc_id(
    mock_edinet_client_context: AsyncMock,
) -> None:
    from kabukit.sources.edinet.concurrent import get_documents

    await get_documents("doc1", pdf=True)

    mock_edinet_client_context.get_document.assert_awaited_once_with("doc1", pdf=True)
