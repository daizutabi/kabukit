from __future__ import annotations

import asyncio
from datetime import date, time
from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from kabukit.sources.datetime import _CalendarCacheManager, _with_date, with_date

if TYPE_CHECKING:
    from typing import Any
    from unittest.mock import AsyncMock, MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


def test_with_date_disclosed() -> None:
    df = pl.DataFrame(
        {
            "DisclosedDate": [
                date(2025, 1, 4),
                date(2025, 1, 4),
                date(2025, 1, 10),
                date(2025, 1, 10),
                date(2025, 1, 10),
            ],
            "DisclosedTime": [
                time(9, 0),
                time(16, 0),
                time(15, 15),
                time(15, 30),
                None,
            ],
            "EPS": [1, 2, 3, 4, 5],
        },
    )

    holidays = [
        date(2025, 1, 1),
        date(2025, 1, 4),
        date(2025, 1, 5),
        date(2025, 1, 11),
        date(2025, 1, 12),
        date(2025, 1, 13),
    ]

    df = _with_date(df, holidays=holidays)
    assert df.columns == ["Date", "DisclosedDate", "DisclosedTime", "EPS"]
    x = df["Date"].to_list()
    assert x[0] == date(2025, 1, 6)
    assert x[1] == date(2025, 1, 6)
    assert x[2] == date(2025, 1, 10)
    assert x[3] == date(2025, 1, 14)
    assert x[4] == date(2025, 1, 14)


def test_with_date_submit() -> None:
    df = pl.DataFrame(
        {
            "SubmittedDate": [
                date(2025, 1, 4),
                date(2025, 1, 4),
                date(2025, 1, 10),
                date(2025, 1, 10),
                date(2025, 1, 10),
            ],
            "SubmittedTime": [
                time(9, 0),
                time(16, 0),
                time(15, 15),
                time(15, 30),
                None,
            ],
            "EPS": [1, 2, 3, 4, 5],
        },
    )

    holidays = [
        date(2025, 1, 1),
        date(2025, 1, 4),
        date(2025, 1, 5),
        date(2025, 1, 11),
        date(2025, 1, 12),
        date(2025, 1, 13),
    ]

    df = _with_date(df, holidays=holidays)
    assert df.columns == ["Date", "SubmittedDate", "SubmittedTime", "EPS"]
    x = df["Date"].to_list()
    assert x[0] == date(2025, 1, 6)
    assert x[1] == date(2025, 1, 6)
    assert x[2] == date(2025, 1, 14)
    assert x[3] == date(2025, 1, 14)
    assert x[4] == date(2025, 1, 14)


def test_with_date_error() -> None:
    with pytest.raises(ValueError, match="DataFrame must contain either "):
        _with_date(pl.DataFrame(), [])


@pytest.fixture(autouse=True)
def reset_cache(mocker: MockerFixture):
    """各テストの実行前にカレンダーキャッシュをリセットする"""

    mocker.patch(
        "kabukit.sources.datetime._calendar_cache_manager",
        _CalendarCacheManager(),
    )


@pytest.fixture
def mock_jquants_client(mocker: MockerFixture):
    return mocker.AsyncMock()


@pytest.fixture
def MockJQuantsClient(mock_jquants_client: AsyncMock, mocker: MockerFixture):
    """datetimeモジュール内で使われるJQuantsClientをモック化する"""
    return mocker.patch(
        "kabukit.sources.jquants.client.JQuantsClient",
        return_value=mocker.MagicMock(
            __aenter__=mocker.AsyncMock(return_value=mock_jquants_client),
            __aexit__=mocker.AsyncMock(),
        ),
    )


async def test_calendar_cache_manager_fetch_and_cache(
    mock_jquants_client: AsyncMock,
    MockJQuantsClient: MagicMock,  # noqa: N803
) -> None:
    """キャッシュマネージャーが初回はデータを取得し、2回目はキャッシュを返すことをテストする"""
    # ここでインポートする理由はfixtureの影響を受けるため
    from kabukit.sources.datetime import _calendar_cache_manager

    mock_jquants_client.get_calendar.return_value = pl.DataFrame(
        {"Date": [date(2025, 1, 1), date(2025, 1, 2)], "IsHoliday": [True, False]},
    )

    # 1回目の呼び出し
    holidays = await _calendar_cache_manager.get_holidays()
    assert holidays == [date(2025, 1, 1)]
    MockJQuantsClient.assert_called_once()
    mock_jquants_client.get_calendar.assert_awaited_once()

    # 2回目の呼び出し（キャッシュが使われるはず）
    holidays_cached = await _calendar_cache_manager.get_holidays()
    assert holidays_cached == [date(2025, 1, 1)]
    MockJQuantsClient.assert_called_once()
    mock_jquants_client.get_calendar.assert_awaited_once()


async def test_calendar_cache_manager_concurrency(
    mock_jquants_client: AsyncMock,
    MockJQuantsClient: MagicMock,  # noqa: N803
) -> None:
    """複数のコルーチンから同時に呼び出されても、データ取得は一度しか実行されないことをテストする"""
    # ここでインポートする理由はfixtureの影響を受けるため
    from kabukit.sources.datetime import _calendar_cache_manager

    async def slow_get_calendar(*_args: Any, **_kwargs: Any):
        await asyncio.sleep(0.01)  # ネットワーク遅延をシミュレート
        return pl.DataFrame({"Date": [date(2025, 1, 1)], "IsHoliday": [True]})

    mock_jquants_client.get_calendar.side_effect = slow_get_calendar

    # 同時に2つのタスクを実行
    tasks = [
        _calendar_cache_manager.get_holidays(),
        _calendar_cache_manager.get_holidays(),
    ]
    results = await asyncio.gather(*tasks)

    # 両方のタスクが同じ結果を返すことを確認
    assert results[0] == [date(2025, 1, 1)]
    assert results[1] == [date(2025, 1, 1)]

    # データ取得処理（get_calendar）が1度しか呼ばれていないことを確認
    MockJQuantsClient.assert_called_once()
    mock_jquants_client.get_calendar.assert_awaited_once()


async def test_async_with_date(mocker: MockerFixture) -> None:
    """非同期関数 with_date が、依存する関数を正しく呼び出すことをテストする"""

    # 依存する関数をモック化
    mock_get_holidays = mocker.patch(
        "kabukit.sources.datetime._calendar_cache_manager.get_holidays",
        new_callable=mocker.AsyncMock,
        return_value=[date(2025, 1, 6)],
    )
    expected_df = pl.DataFrame({"Date": [date(2025, 1, 6)]})
    mock_internal_with_date = mocker.patch(
        "kabukit.sources.datetime._with_date",
        return_value=expected_df,
    )

    # テスト対象の関数を呼び出し
    input_df = pl.DataFrame({"DisclosedDate": [date(2025, 1, 4)]})
    result_df = await with_date(input_df)

    # モックが期待通りに呼ばれたか確認
    mock_get_holidays.assert_awaited_once()
    mock_internal_with_date.assert_called_once()

    # _with_dateの引数を個別にチェック
    assert input_df.equals(mock_internal_with_date.call_args[0][0])
    assert [date(2025, 1, 6)] == mock_internal_with_date.call_args[0][1]

    # 最終的な返り値が正しいか確認
    assert_frame_equal(result_df, expected_df)
