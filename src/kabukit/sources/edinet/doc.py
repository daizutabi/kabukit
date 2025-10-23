from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl

from kabukit.utils.datetime import strpdate

if TYPE_CHECKING:
    import datetime


def clean_list(df: pl.DataFrame, date: str | datetime.date) -> pl.DataFrame:
    if isinstance(date, str):
        date = strpdate(date)

    null_columns = [c for c in df.columns if df[c].dtype == pl.Null]

    return (
        df.with_columns(
            pl.col(null_columns).cast(pl.String),
        )
        .with_columns(
            pl.lit(date).alias("Date"),
            pl.col("^.+DateTime$").str.to_datetime(
                "%Y-%m-%d %H:%M",
                strict=False,
                time_zone="Asia/Tokyo",
            ),
            pl.col("^period.+$").str.to_date("%Y-%m-%d", strict=False),
            pl.col("^.+Flag$").cast(pl.Int8).cast(pl.Boolean),
            pl.col("^.+Code$").cast(pl.String),
        )
        .rename({"secCode": "Code"})
        .select("Date", "Code", pl.exclude("Date", "Code"))
    )


def clean_pdf(content: bytes, doc_id: str) -> pl.DataFrame:
    return pl.DataFrame({"docID": [doc_id], "pdf": [content]})


def read_csv(data: bytes) -> pl.DataFrame:
    return pl.read_csv(
        data,
        separator="\t",
        encoding="utf-16-le",
        infer_schema_length=None,
    )


def clean_csv(df: pl.DataFrame, doc_id: str) -> pl.DataFrame:
    return df.select(
        pl.lit(doc_id).alias("docID"),
        pl.all(),
    )
