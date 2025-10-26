from __future__ import annotations

import polars as pl


def read_csv(data: bytes) -> pl.DataFrame:
    return pl.read_csv(
        data,
        separator="\t",
        encoding="utf-16-le",
        infer_schema_length=None,
    )
