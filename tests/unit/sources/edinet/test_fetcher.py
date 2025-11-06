from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from kabukit.sources.edinet.client import EdinetClient
from kabukit.sources.edinet.fetcher import get_documents, get_list

if TYPE_CHECKING:
    from collections.abc import Iterable
    from unittest.mock import AsyncMock, MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


def dummy_progress(x: Iterable[Any]) -> Iterable[Any]:
    return x


@pytest.fixture
def mock_get_past_dates(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.sources.edinet.fetcher.get_past_dates")


@pytest.fixture
def mock_edinet_client(mocker: MockerFixture) -> AsyncMock:
    """EdinetClientの非同期コンテキストマネージャをモックするフィクスチャ"""
    mock_client_instance = mocker.AsyncMock()
    mocker.patch(
        "kabukit.sources.edinet.fetcher.EdinetClient",
        return_value=mocker.MagicMock(
            __aenter__=mocker.AsyncMock(return_value=mock_client_instance),
            __aexit__=mocker.AsyncMock(),
        ),
    )
    return mock_client_instance


async def test_get_list_single_date(mock_edinet_client: AsyncMock) -> None:
    target_date = datetime.date(2025, 10, 10)
    await get_list(target_date)

    mock_edinet_client.get_list.assert_awaited_once_with(target_date)


async def test_get_documents_single_doc_id(mock_edinet_client: AsyncMock) -> None:
    await get_documents("doc1", pdf=True)

    mock_edinet_client.get_document.assert_awaited_once_with("doc1", pdf=True)


async def test_get_list_days(
    mock_get_past_dates: MagicMock,
    mock_fetcher_get: AsyncMock,
) -> None:
    mock_get_past_dates.return_value = [
        datetime.date(2023, 1, 3),
        datetime.date(2023, 1, 2),
        datetime.date(2023, 1, 1),
    ]
    mock_fetcher_get.return_value = pl.DataFrame({"Date": [2], "Code": ["10000"]})

    result = await get_list(
        days=3,
        max_items=2,
        max_concurrency=5,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
    )

    assert_frame_equal(result, pl.DataFrame({"Date": [2], "Code": ["10000"]}))

    mock_get_past_dates.assert_called_once_with(days=3, years=None)
    mock_fetcher_get.assert_awaited_once_with(
        EdinetClient,
        EdinetClient.get_list,
        [
            datetime.date(2023, 1, 3),
            datetime.date(2023, 1, 2),
            datetime.date(2023, 1, 1),
        ],
        max_items=2,
        max_concurrency=5,
        progress=dummy_progress,
    )


async def test_get_list_years(
    mock_get_past_dates: MagicMock,
    mock_fetcher_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    mock_get_past_dates.return_value = [
        datetime.date(2023, 1, 1),
        datetime.date(2022, 1, 1),
    ]
    mock_fetcher_get.return_value = pl.DataFrame({"Date": [1], "Code": ["10000"]})

    await get_list(years=2)

    mock_get_past_dates.assert_called_once_with(days=None, years=2)
    mock_fetcher_get.assert_awaited_once_with(
        EdinetClient,
        EdinetClient.get_list,
        [
            datetime.date(2023, 1, 1),
            datetime.date(2022, 1, 1),
        ],
        max_items=None,
        max_concurrency=mocker.ANY,
        progress=None,
    )


async def test_get_list_invalid_date(mock_fetcher_get: AsyncMock) -> None:
    mock_fetcher_get.return_value = pl.DataFrame()

    result = await get_list(["2025-10-10"])
    assert result.is_empty()


async def test_get_documents_csv(mock_fetcher_get: AsyncMock) -> None:
    mock_fetcher_get.return_value = pl.DataFrame({"DocumentId": [3]})

    result = await get_documents(
        ["doc1", "doc2", "doc3"],
        max_items=2,
        max_concurrency=5,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
    )

    assert_frame_equal(result, pl.DataFrame({"DocumentId": [3]}))

    mock_fetcher_get.assert_awaited_once_with(
        EdinetClient,
        EdinetClient.get_csv,
        ["doc1", "doc2", "doc3"],
        max_items=2,
        max_concurrency=5,
        progress=dummy_progress,
    )


async def test_get_documents_pdf(
    mock_fetcher_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    mock_fetcher_get.return_value = pl.DataFrame({"DocumentId": [1]})

    await get_documents(["doc1", "doc2"], pdf=True)

    mock_fetcher_get.assert_awaited_once_with(
        EdinetClient,
        EdinetClient.get_pdf,
        ["doc1", "doc2"],
        max_items=None,
        max_concurrency=mocker.ANY,
        progress=None,
    )
