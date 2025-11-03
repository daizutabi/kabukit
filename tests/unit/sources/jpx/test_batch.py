from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from kabukit.sources.jpx.batch import get_shares
from kabukit.sources.jpx.client import JpxClient

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
def jpx_client_class_mock(mocker: MockerFixture) -> MagicMock:
    """JpxClientクラスをモックし、そのモックオブジェクトを返すフィクスチャ"""
    mock_client_instance = mocker.AsyncMock(spec=JpxClient)

    async def mock_iter_pdf_urls():
        yield "url1.pdf"
        yield "url2.pdf"

    mock_client_instance.iter_shares_pdf_urls = mocker.MagicMock(
        return_value=mock_iter_pdf_urls(),
    )

    class_mock = mocker.patch(
        "kabukit.sources.jpx.batch.JpxClient",
        return_value=mocker.MagicMock(
            __aenter__=mocker.AsyncMock(return_value=mock_client_instance),
            __aexit__=mocker.AsyncMock(),
        ),
    )
    # NOTE: clientインスタンスも属性として持たせておく
    class_mock.mock_client_instance = mock_client_instance
    return class_mock


async def test_get_shares(
    jpx_client_class_mock: MagicMock,
    mock_gather_get: AsyncMock,
) -> None:
    mock_gather_get.return_value = pl.DataFrame({"Code": ["B", "A"], "Date": [2, 1]})

    result = await get_shares(
        max_items=10,
        max_concurrency=5,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    jpx_client_class_mock.mock_client_instance.iter_shares_pdf_urls.assert_called_once()

    expected_pdf_urls = ["url1.pdf", "url2.pdf"]
    mock_gather_get.assert_awaited_once_with(
        jpx_client_class_mock,  # クラスのモックオブジェクトで比較
        "shares",
        expected_pdf_urls,
        max_items=10,
        max_concurrency=5,
        progress=dummy_progress,
        callback=dummy_callback,
    )

    expected_df = pl.DataFrame({"Code": ["A", "B"], "Date": [1, 2]})
    assert_frame_equal(result, expected_df)


async def test_get_shares_empty(
    jpx_client_class_mock: MagicMock,  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
    mock_gather_get: AsyncMock,
) -> None:
    mock_gather_get.return_value = pl.DataFrame()

    result = await get_shares()

    assert result.is_empty()
    mock_gather_get.assert_awaited_once()
