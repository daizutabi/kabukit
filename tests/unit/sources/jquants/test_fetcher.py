from __future__ import annotations

from typing import TYPE_CHECKING, Any

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from kabukit.sources.jquants.client import JQuantsClient
from kabukit.sources.jquants.fetcher import (
    get_calendar,
    get_info,
    get_prices,
    get_statements,
    get_target_codes,
)

if TYPE_CHECKING:
    from collections.abc import Iterable
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_jquants_client(mocker: MockerFixture) -> AsyncMock:
    """JQuantsClientの非同期コンテキストマネージャをモックするフィクスチャ"""
    mock_client_instance = mocker.AsyncMock()
    mocker.patch(
        "kabukit.sources.jquants.fetcher.JQuantsClient",
        return_value=mocker.MagicMock(
            __aenter__=mocker.AsyncMock(return_value=mock_client_instance),
            __aexit__=mocker.AsyncMock(),
        ),
    )
    return mock_client_instance


async def test_get_calendar(mock_jquants_client: AsyncMock) -> None:
    await get_calendar()

    mock_jquants_client.get_calendar.assert_awaited_once()


async def test_get_info(mock_jquants_client: AsyncMock) -> None:
    await get_info()

    mock_jquants_client.get_info.assert_awaited_once_with(
        None,
        None,
        only_common_stocks=True,
    )


async def test_get_info_with_code(mock_jquants_client: AsyncMock) -> None:
    await get_info("7203")

    mock_jquants_client.get_info.assert_awaited_once_with(
        "7203",
        None,
        only_common_stocks=True,
    )


async def test_get_info_with_date(mock_jquants_client: AsyncMock) -> None:
    await get_info(date="2025-10-10")

    mock_jquants_client.get_info.assert_awaited_once_with(
        None,
        "2025-10-10",
        only_common_stocks=True,
    )


@pytest.fixture
def mock_get_info(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jquants.fetcher.get_info",
        new_callable=mocker.AsyncMock,
    )


async def test_get_target_codes(mock_get_info: AsyncMock) -> None:
    mock_df = pl.DataFrame({"Code": ["0001", "0002"]})
    mock_get_info.return_value = mock_df

    result = await get_target_codes()

    mock_get_info.assert_awaited_once_with(only_common_stocks=True)
    assert result == ["0001", "0002"]


@pytest.fixture
def mock_get_target_codes(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jquants.fetcher.get_target_codes",
        new_callable=mocker.AsyncMock,
    )


def dummy_progress(x: Iterable[Any]) -> Iterable[Any]:
    return x


async def test_get_statements_with_code(mock_jquants_client: AsyncMock) -> None:
    await get_statements("7203")

    mock_jquants_client.get_statements.assert_awaited_once_with("7203", None)


async def test_get_statements_with_date(mock_jquants_client: AsyncMock) -> None:
    await get_statements(date="2025-10-10")

    mock_jquants_client.get_statements.assert_awaited_once_with(None, "2025-10-10")


async def test_get_statements_with_codes(
    mock_fetcher_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    mock_fetcher_get.return_value = pl.DataFrame(
        {"Date": [4, 3, 2, 1], "Code": [2, 1, 2, 1]},
    )

    result = await get_statements(
        ["1111", "2222"],
        max_items=10,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
    )

    assert_frame_equal(
        result,
        pl.DataFrame({"Date": [1, 3, 2, 4], "Code": [1, 1, 2, 2]}),
    )

    mock_fetcher_get.assert_awaited_once_with(
        JQuantsClient,
        JQuantsClient.get_statements,
        ["1111", "2222"],
        max_items=10,
        max_concurrency=mocker.ANY,
        progress=dummy_progress,
    )


async def test_get_statements(
    mock_get_target_codes: AsyncMock,
    mock_fetcher_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    mock_get_target_codes.return_value = ["1111", "2222", "3333"]
    mock_fetcher_get.return_value = pl.DataFrame(
        {"Date": [4, 3, 2, 1], "Code": [2, 1, 2, 1]},
    )

    result = await get_statements()

    assert_frame_equal(
        result,
        pl.DataFrame({"Date": [1, 3, 2, 4], "Code": [1, 1, 2, 2]}),
    )

    mock_get_target_codes.assert_awaited_once()
    mock_fetcher_get.assert_awaited_once_with(
        JQuantsClient,
        JQuantsClient.get_statements,
        ["1111", "2222", "3333"],
        max_items=None,
        max_concurrency=mocker.ANY,
        progress=None,
    )


async def test_get_prices_with_code(mock_jquants_client: AsyncMock) -> None:
    await get_prices("7203")

    mock_jquants_client.get_prices.assert_awaited_once_with("7203", None)


async def test_get_prices_with_date(mock_jquants_client: AsyncMock) -> None:
    await get_prices(date="2025-10-10")

    mock_jquants_client.get_prices.assert_awaited_once_with(None, "2025-10-10")


async def test_get_prices_with_codes(mock_fetcher_get: AsyncMock) -> None:
    mock_fetcher_get.return_value = pl.DataFrame(
        {"Date": [4, 3, 2, 1], "Code": [2, 1, 2, 1]},
    )

    result = await get_prices(
        ["3333", "4444"],
        max_items=5,
        max_concurrency=20,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
    )

    assert_frame_equal(
        result,
        pl.DataFrame({"Date": [1, 3, 2, 4], "Code": [1, 1, 2, 2]}),
    )

    mock_fetcher_get.assert_awaited_once_with(
        JQuantsClient,
        JQuantsClient.get_prices,
        ["3333", "4444"],
        max_items=5,
        max_concurrency=20,
        progress=dummy_progress,
    )


async def test_get_prices(
    mock_get_target_codes: AsyncMock,
    mock_fetcher_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    mock_get_target_codes.return_value = ["1111", "2222", "3333"]
    mock_fetcher_get.return_value = pl.DataFrame(
        {"Date": [4, 3, 2, 1], "Code": [2, 1, 2, 1]},
    )

    result = await get_prices()

    assert_frame_equal(
        result,
        pl.DataFrame({"Date": [1, 3, 2, 4], "Code": [1, 1, 2, 2]}),
    )

    mock_get_target_codes.assert_awaited_once()
    mock_fetcher_get.assert_awaited_once_with(
        JQuantsClient,
        JQuantsClient.get_prices,
        ["1111", "2222", "3333"],
        max_items=None,
        max_concurrency=mocker.ANY,
        progress=None,
    )
