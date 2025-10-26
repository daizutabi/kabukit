from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl

if TYPE_CHECKING:
    import datetime


def transform_list(df: pl.DataFrame, date: datetime.date) -> pl.DataFrame:
    return df.select(
        pl.col("Code"),
        pl.lit(date).alias("DisclosedDate"),
        pl.exclude("Code"),
    )
