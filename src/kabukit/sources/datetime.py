from __future__ import annotations

import datetime

import polars as pl


def with_date(df: pl.DataFrame, holidays: list[datetime.date]) -> pl.DataFrame:
    """`Date`列を追加する。

    開示日が休日のとき、あるいは、開示時刻が15時30分以降の場合、Dateを開示日の翌営業日に設定する。
    """
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
