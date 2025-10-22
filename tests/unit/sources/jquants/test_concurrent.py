from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest

from kabukit.sources.jquants.client import JQuantsClient

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


def dummy_progress(x: Iterable[Any]) -> Iterable[Any]:
    return x


def dummy_callback(df: pl.DataFrame) -> pl.DataFrame:
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
        "kabukit.sources.jquants.concurrent.get_target_codes",
        new_callable=mocker.AsyncMock,
    )


@pytest.fixture
def mock_get_info(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jquants.concurrent.get_info",
        new_callable=mocker.AsyncMock,
    )


@pytest.mark.asyncio
async def test_get(mock_utils_get: AsyncMock) -> None:
    from kabukit.sources.jquants.concurrent import get

    mock_utils_get.return_value = pl.DataFrame(
        {"Date": [4, 3, 2, 1], "Code": ["a", "b", "b", "a"]},
    )

    result = await get(
        "test_resource",
        ["1234", "5678"],
        max_concurrency=10,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    expected = pl.DataFrame({"Date": [1, 4, 2, 3], "Code": ["a", "a", "b", "b"]})
    assert result.equals(expected)

    mock_utils_get.assert_awaited_once_with(
        JQuantsClient,
        "test_resource",
        ["1234", "5678"],
        max_items=None,
        max_concurrency=10,
        progress=dummy_progress,
        callback=dummy_callback,
    )


@pytest.mark.asyncio
async def test_get_without_codes(
    mock_utils_get: AsyncMock,
    mock_get_target_codes: AsyncMock,
) -> None:
    from kabukit.sources.jquants.concurrent import get

    mock_get_target_codes.return_value = ["1111", "2222", "3333"]
    # get() は .sort("Code", "Date") を行うので、モックの戻り値にもカラムが必要
    mock_utils_get.return_value = pl.DataFrame(
        {"Date": [1], "Code": ["c"], "b": [2]},
    )

    result = await get(
        "test_resource",
        None,  # codes=None を明示的に渡す
        max_items=2,
        max_concurrency=5,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    # ソート後の結果を期待値とする
    expected = pl.DataFrame({"Date": [1], "Code": ["c"], "b": [2]})
    assert result.equals(expected)

    mock_get_target_codes.assert_awaited_once()
    mock_utils_get.assert_awaited_once_with(
        JQuantsClient,
        "test_resource",
        ["1111", "2222", "3333"],  # get_target_codes の結果が渡される
        max_items=2,
        max_concurrency=5,
        progress=dummy_progress,
        callback=dummy_callback,
    )


@pytest.mark.asyncio
async def test_get_calendar(mock_jquants_client_context: AsyncMock) -> None:
    from kabukit.sources.jquants.concurrent import get_calendar

    await get_calendar()

    mock_jquants_client_context.get_calendar.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_info(mock_jquants_client_context: AsyncMock) -> None:
    from kabukit.sources.jquants.concurrent import get_info

    await get_info("7203")

    mock_jquants_client_context.get_info.assert_awaited_once_with("7203")


@pytest.mark.asyncio
async def test_get_target_codes(mock_get_info: AsyncMock) -> None:
    from kabukit.sources.jquants.concurrent import get_target_codes

    mock_df = pl.DataFrame(
        {
            "Code": ["0001", "0002", "0003", "0004", "0005"],
            "MarketCodeName": [
                "プライム",
                "TOKYO PRO MARKET",  # フィルタリング対象
                "スタンダード",
                "グロース",
                "プライム",
            ],
            "Sector17CodeName": [
                "情報・通信業",
                "サービス業",
                "その他",  # フィルタリング対象
                "小売業",
                "銀行業",
            ],
            "CompanyName": [
                "A社",
                "B社",
                "C社",
                "D（優先株式）",  # フィルタリング対象
                "E社",
            ],
        },
    )
    mock_get_info.return_value = mock_df

    result = await get_target_codes()

    mock_get_info.assert_awaited_once_with()
    assert result == ["0001", "0005"]


@pytest.mark.asyncio
async def test_get_statements(mocker: MockerFixture) -> None:
    from kabukit.sources.jquants.concurrent import get_statements

    mock_get = mocker.patch(
        "kabukit.sources.jquants.concurrent.get",
        new_callable=mocker.AsyncMock,
    )

    await get_statements(
        ["1111", "2222"],
        max_items=10,
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    mock_get.assert_awaited_once_with(
        "statements",
        ["1111", "2222"],
        max_items=10,
        max_concurrency=12,  # get_statements のデフォルト値
        progress=dummy_progress,
        callback=dummy_callback,
    )


@pytest.mark.asyncio
async def test_get_statements_with_single_code(
    mock_jquants_client_context: AsyncMock,
) -> None:
    from kabukit.sources.jquants.concurrent import get_statements

    await get_statements("7203")

    mock_jquants_client_context.get_statements.assert_awaited_once_with("7203")


@pytest.mark.asyncio
async def test_get_prices(mocker: MockerFixture) -> None:
    from kabukit.sources.jquants.concurrent import get_prices

    mock_get = mocker.patch(
        "kabukit.sources.jquants.concurrent.get",
        new_callable=mocker.AsyncMock,
    )

    await get_prices(
        ["3333", "4444"],
        max_items=5,
        max_concurrency=20,  # デフォルト(8)を上書き
        progress=dummy_progress,  # pyright: ignore[reportArgumentType]
        callback=dummy_callback,
    )

    mock_get.assert_awaited_once_with(
        "prices",
        ["3333", "4444"],
        max_items=5,
        max_concurrency=20,  # 上書きされた値
        progress=dummy_progress,
        callback=dummy_callback,
    )


@pytest.mark.asyncio
async def test_get_prices_with_single_code(
    mock_jquants_client_context: AsyncMock,
) -> None:
    from kabukit.sources.jquants.concurrent import get_prices

    await get_prices("7203")

    mock_jquants_client_context.get_prices.assert_awaited_once_with("7203")
