from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from kabukit.sources.edinet.client import EdinetClient

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any
    from unittest.mock import AsyncMock, MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


def dummy_progress(x: Iterable[Any]) -> Iterable[Any]:
    return x


def dummy_callback(df: pl.DataFrame) -> pl.DataFrame:
    return df


@pytest.fixture
def mock_get(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.utils.concurrent.get", new_callable=mocker.AsyncMock)


@pytest.fixture
def mock_get_past_dates(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.sources.edinet.concurrent.get_past_dates")


@pytest.mark.asyncio
async def test_get_list_days(
    mock_get_past_dates: MagicMock,
    mock_get: AsyncMock,
) -> None:
    from kabukit.sources.edinet.concurrent import get_list

    mock_get_past_dates.return_value = [
        datetime.date(2023, 1, 3),
        datetime.date(2023, 1, 2),
        datetime.date(2023, 1, 1),
    ]
    mock_get.return_value = pl.DataFrame({"Date": [2], "Code": ["10000"]})

    result = await get_list(
        days=3,
        max_items=2,
        max_concurrency=5,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    assert_frame_equal(result, pl.DataFrame({"Date": [2], "Code": ["10000"]}))

    mock_get_past_dates.assert_called_once_with(days=3, years=None)
    mock_get.assert_awaited_once_with(
        EdinetClient,
        "list",
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
async def test_get_list_years(
    mock_get_past_dates: MagicMock,
    mock_get: AsyncMock,
) -> None:
    from kabukit.sources.edinet.concurrent import get_list

    mock_get_past_dates.return_value = [
        datetime.date(2023, 1, 1),
        datetime.date(2022, 1, 1),
    ]
    mock_get.return_value = pl.DataFrame({"Date": [1], "Code": ["10000"]})

    await get_list(years=2)

    mock_get_past_dates.assert_called_once_with(days=None, years=2)
    mock_get.assert_awaited_once_with(
        EdinetClient,
        "list",
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
async def test_get_list_single_date(mock_edinet_client: AsyncMock) -> None:
    from kabukit.sources.edinet.concurrent import get_list

    target_date = datetime.date(2025, 10, 10)
    await get_list(target_date)

    mock_edinet_client.get_list.assert_awaited_once_with(target_date)


@pytest.mark.asyncio
async def test_get_list_invalid_date(mock_get: AsyncMock) -> None:
    from kabukit.sources.edinet.concurrent import get_list

    mock_get.return_value = pl.DataFrame()

    result = await get_list(["2025-10-10"])
    assert result.is_empty()


@pytest.mark.asyncio
async def test_get_documents_csv(mock_get: AsyncMock) -> None:
    from kabukit.sources.edinet.concurrent import get_documents

    mock_get.return_value = pl.DataFrame({"docID": [3]})

    result = await get_documents(
        ["doc1", "doc2", "doc3"],
        max_items=2,
        max_concurrency=5,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    assert_frame_equal(result, pl.DataFrame({"docID": [3]}))

    mock_get.assert_awaited_once_with(
        EdinetClient,
        "csv",
        ["doc1", "doc2", "doc3"],
        max_items=2,
        max_concurrency=5,
        progress=dummy_progress,
        callback=dummy_callback,
    )


@pytest.mark.asyncio
async def test_get_documents_pdf(mock_get: AsyncMock) -> None:
    from kabukit.sources.edinet.concurrent import get_documents

    mock_get.return_value = pl.DataFrame({"docID": [1]})

    await get_documents(["doc1", "doc2"], pdf=True)

    mock_get.assert_awaited_once_with(
        EdinetClient,
        "pdf",
        ["doc1", "doc2"],
        max_items=None,
        max_concurrency=None,
        progress=None,
        callback=None,
    )


@pytest.mark.asyncio
async def test_get_documents_single_doc_id(
    mock_edinet_client: AsyncMock,
) -> None:
    from kabukit.sources.edinet.concurrent import get_documents

    await get_documents("doc1", pdf=True)

    mock_edinet_client.get_document.assert_awaited_once_with("doc1", pdf=True)
