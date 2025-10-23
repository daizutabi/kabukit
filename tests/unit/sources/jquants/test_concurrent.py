from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from kabukit.sources.jquants.client import JQuantsClient

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_calendar(mock_jquants_client: AsyncMock) -> None:
    from kabukit.sources.jquants.concurrent import get_calendar

    await get_calendar()

    mock_jquants_client.get_calendar.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_info(mock_jquants_client: AsyncMock) -> None:
    from kabukit.sources.jquants.concurrent import get_info

    await get_info()

    mock_jquants_client.get_info.assert_awaited_once_with(
        None,
        None,
        only_common_stocks=True,
    )


@pytest.mark.asyncio
async def test_get_info_with_code(mock_jquants_client: AsyncMock) -> None:
    from kabukit.sources.jquants.concurrent import get_info

    await get_info("7203")

    mock_jquants_client.get_info.assert_awaited_once_with(
        "7203",
        None,
        only_common_stocks=True,
    )


@pytest.mark.asyncio
async def test_get_info_with_date(mock_jquants_client: AsyncMock) -> None:
    from kabukit.sources.jquants.concurrent import get_info

    await get_info(date="2025-10-10")

    mock_jquants_client.get_info.assert_awaited_once_with(
        None,
        "2025-10-10",
        only_common_stocks=True,
    )


@pytest.fixture
def mock_get_info(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jquants.concurrent.get_info",
        new_callable=mocker.AsyncMock,
    )


@pytest.mark.asyncio
async def test_get_target_codes(mock_get_info: AsyncMock) -> None:
    from kabukit.sources.jquants.concurrent import get_target_codes

    mock_df = pl.DataFrame({"Code": ["0001", "0002"]})
    mock_get_info.return_value = mock_df

    result = await get_target_codes()

    mock_get_info.assert_awaited_once_with(only_common_stocks=True)
    assert result == ["0001", "0002"]


@pytest.fixture
def mock_get(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.utils.concurrent.get", new_callable=mocker.AsyncMock)


@pytest.fixture
def mock_get_target_codes(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jquants.concurrent.get_target_codes",
        new_callable=mocker.AsyncMock,
    )


def dummy_progress(x: Iterable[Any]) -> Iterable[Any]:
    return x


def dummy_callback(df: pl.DataFrame) -> pl.DataFrame:
    return df


@pytest.mark.asyncio
async def test_get_statements_with_code(mock_jquants_client: AsyncMock) -> None:
    from kabukit.sources.jquants.concurrent import get_statements

    await get_statements("7203")

    mock_jquants_client.get_statements.assert_awaited_once_with("7203", None)


@pytest.mark.asyncio
async def test_get_statements_with_date(mock_jquants_client: AsyncMock) -> None:
    from kabukit.sources.jquants.concurrent import get_statements

    await get_statements(date="2025-10-10")

    mock_jquants_client.get_statements.assert_awaited_once_with(None, "2025-10-10")


@pytest.mark.asyncio
async def test_get_statements_with_codes(mock_get: AsyncMock) -> None:
    from kabukit.sources.jquants.concurrent import get_statements

    mock_get.return_value = pl.DataFrame({"Date": [4, 3, 2, 1], "Code": [2, 1, 2, 1]})

    result = await get_statements(
        ["1111", "2222"],
        max_items=10,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    assert_frame_equal(
        result,
        pl.DataFrame({"Date": [1, 3, 2, 4], "Code": [1, 1, 2, 2]}),
    )

    mock_get.assert_awaited_once_with(
        JQuantsClient,
        "statements",
        ["1111", "2222"],
        max_items=10,
        max_concurrency=12,
        progress=dummy_progress,
        callback=dummy_callback,
    )


@pytest.mark.asyncio
async def test_get_statements(
    mock_get: AsyncMock,
    mock_get_target_codes: AsyncMock,
) -> None:
    from kabukit.sources.jquants.concurrent import get_statements

    mock_get_target_codes.return_value = ["1111", "2222", "3333"]
    mock_get.return_value = pl.DataFrame({"Date": [4, 3, 2, 1], "Code": [2, 1, 2, 1]})

    result = await get_statements()

    assert_frame_equal(
        result,
        pl.DataFrame({"Date": [1, 3, 2, 4], "Code": [1, 1, 2, 2]}),
    )

    mock_get_target_codes.assert_awaited_once()
    mock_get.assert_awaited_once_with(
        JQuantsClient,
        "statements",
        ["1111", "2222", "3333"],
        max_items=None,
        max_concurrency=12,
        progress=None,
        callback=None,
    )


@pytest.mark.asyncio
async def test_get_prices_with_code(mock_jquants_client: AsyncMock) -> None:
    from kabukit.sources.jquants.concurrent import get_prices

    await get_prices("7203")

    mock_jquants_client.get_prices.assert_awaited_once_with("7203", None)


@pytest.mark.asyncio
async def test_get_prices_with_date(mock_jquants_client: AsyncMock) -> None:
    from kabukit.sources.jquants.concurrent import get_prices

    await get_prices(date="2025-10-10")

    mock_jquants_client.get_prices.assert_awaited_once_with(None, "2025-10-10")


@pytest.mark.asyncio
async def test_get_prices_with_codes(mock_get: AsyncMock) -> None:
    from kabukit.sources.jquants.concurrent import get_prices

    mock_get.return_value = pl.DataFrame({"Date": [4, 3, 2, 1], "Code": [2, 1, 2, 1]})

    result = await get_prices(
        ["3333", "4444"],
        max_items=5,
        max_concurrency=20,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    assert_frame_equal(
        result,
        pl.DataFrame({"Date": [1, 3, 2, 4], "Code": [1, 1, 2, 2]}),
    )

    mock_get.assert_awaited_once_with(
        JQuantsClient,
        "prices",
        ["3333", "4444"],
        max_items=5,
        max_concurrency=20,
        progress=dummy_progress,
        callback=dummy_callback,
    )


@pytest.mark.asyncio
async def test_get_prices(
    mock_get: AsyncMock,
    mock_get_target_codes: AsyncMock,
) -> None:
    from kabukit.sources.jquants.concurrent import get_prices

    mock_get_target_codes.return_value = ["1111", "2222", "3333"]
    mock_get.return_value = pl.DataFrame({"Date": [4, 3, 2, 1], "Code": [2, 1, 2, 1]})

    result = await get_prices()

    assert_frame_equal(
        result,
        pl.DataFrame({"Date": [1, 3, 2, 4], "Code": [1, 1, 2, 2]}),
    )

    mock_get_target_codes.assert_awaited_once()
    mock_get.assert_awaited_once_with(
        JQuantsClient,
        "prices",
        ["1111", "2222", "3333"],
        max_items=None,
        max_concurrency=8,
        progress=None,
        callback=None,
    )
