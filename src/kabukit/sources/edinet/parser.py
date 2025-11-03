from __future__ import annotations

import polars as pl


def parse_pdf(content: bytes, doc_id: str) -> pl.DataFrame:
    return pl.DataFrame({"DocumentId": [doc_id], "PdfContent": [content]})


def parse_csv(content: bytes, doc_id: str) -> pl.DataFrame:
    return read_csv(content).select(
        pl.lit(doc_id).alias("DocumentId"),
        pl.all(),
    )


def read_csv(content: bytes) -> pl.DataFrame:
    return pl.read_csv(
        content,
        separator="\t",
        encoding="utf-16-le",
        infer_schema_length=None,
    )
