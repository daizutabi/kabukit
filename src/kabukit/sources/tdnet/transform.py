from __future__ import annotations

import polars as pl

from kabukit.sources.utils import normalize_code


def transform_list(df: pl.DataFrame) -> pl.DataFrame:
    null_columns = [c for c in df.columns if df[c].dtype == pl.Null]

    return df.with_columns(
        pl.col(null_columns).cast(pl.String),
    ).pipe(normalize_code)
