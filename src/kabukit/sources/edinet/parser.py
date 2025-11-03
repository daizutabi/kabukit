from __future__ import annotations

import re

import polars as pl

from kabukit.sources.utils import extract_content


def parse_pdf(content: bytes, doc_id: str) -> pl.DataFrame:
    return pl.DataFrame({"DocumentId": [doc_id], "PdfContent": [content]})


def parse_xbrl(content: bytes) -> str | None:
    pattern = re.compile(r"^XBRL/PublicDoc/.+\.xbrl$")

    if xbrl := extract_content(content, pattern):
        return xbrl.decode("utf-8")

    return None


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
