from __future__ import annotations

import asyncio
import datetime
from typing import final

import polars as pl

# pyright: reportImportCycles=false


@final
class _CalendarCacheManager:
    def __init__(self) -> None:
        self._holidays: list[datetime.date] | None = None
        self._lock = asyncio.Lock()

    async def get_holidays(self) -> list[datetime.date]:
        from kabukit.sources.jquants.client import JQuantsClient

        async with self._lock:
            if self._holidays is None:
                async with JQuantsClient() as client:
                    df = await client.get_calendar()

                holidays = df.filter(pl.col("IsHoliday"))["Date"]
                self._holidays = holidays.to_list()

            return self._holidays


_calendar_cache_manager = _CalendarCacheManager()


async def with_date(df: pl.DataFrame) -> pl.DataFrame:
    """`Date`列を追加する。

    開示日が休日のとき、または、開示時刻が15時30分以降の場合、Dateを開示日の翌営業日に設定する。
    """
    holidays = await _calendar_cache_manager.get_holidays()
    return _with_date(df, holidays)


def _with_date(df: pl.DataFrame, holidays: list[datetime.date]) -> pl.DataFrame:
    is_after_hours = pl.col("DisclosedTime").is_null() | (
        pl.col("DisclosedTime") >= datetime.time(15, 30)
    )

    return df.select(
        pl.when(is_after_hours)
        .then(pl.col("DisclosedDate") + datetime.timedelta(days=1))
        .otherwise(pl.col("DisclosedDate"))
        .dt.add_business_days(0, holidays=holidays, roll="forward")
        .alias("Date"),
        pl.all(),
    )
