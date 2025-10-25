from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl

from kabukit.utils.datetime import strpdate

if TYPE_CHECKING:
    import datetime


def clean_list(df: pl.DataFrame, date: str | datetime.date) -> pl.DataFrame:
    df = filter_list(df)

    if df.is_empty():
        return df

    df = rename_list(df)

    null_columns = [c for c in df.columns if df[c].dtype == pl.Null]

    file_date = strpdate(date) if isinstance(date, str) else date

    return (
        df.with_columns(
            pl.col(null_columns).cast(pl.String),
        )
        .with_columns(
            pl.col("^.*Code$").cast(pl.String),
            pl.col("SubmittedDateTime").str.to_datetime(
                "%Y-%m-%d %H:%M",
                strict=False,
                time_zone="Asia/Tokyo",
            ),
            pl.col("^Period.+$").str.to_date("%Y-%m-%d", strict=False),
            pl.col("^.+Status$").cast(pl.UInt8),
            pl.col("^.+Flag$").cast(pl.Int8).cast(pl.Boolean),
            pl.lit(file_date).alias("FileDate"),
        )
        .with_columns(
            pl.col("SubmittedDateTime").dt.date().alias("SubmittedDate"),
            pl.col("SubmittedDateTime").dt.time().alias("SubmittedTime"),
        )
        .drop("SubmittedDateTime")
        .select("Code", "^Submitted.+$", pl.exclude("Code", "^Submitted.+$"))
    )


def filter_list(df: pl.DataFrame) -> pl.DataFrame:
    return df.filter(
        pl.col("secCode").is_not_null(),
        pl.col("fundCode").is_null(),
    )


def rename_list(df: pl.DataFrame) -> pl.DataFrame:
    """書類一覧のカラム名をライブラリの命名規則に沿ってリネームし、不要なカラムを削除する。"""
    mapping = {
        "secCode": "Code",
        "submitDateTime": "SubmittedDateTime",
        "filerName": "Company",
        "docID": "DocumentId",
        "docTypeCode": "DocumentTypeCode",
        "docDescription": "DocumentDescription",
        "currentReportReason": "CurrentReportReason",
        "periodStart": "PeriodStart",
        "periodEnd": "PeriodEnd",
        "edinetCode": "EdinetCode",
        "issuerEdinetCode": "IssuerEdinetCode",
        "subjectEdinetCode": "SubjectEdinetCode",
        "subsidiaryEdinetCode": "SubsidiaryEdinetCode",
        "parentDocID": "ParentDocumentId",
        "disclosureStatus": "DisclosureStatus",
        "docInfoEditStatus": "DocumentInfoEditStatus",
        "legalStatus": "LegalStatus",
        "withdrawalStatus": "WithdrawalStatus",
        "attachDocFlag": "AttachDocumentFlag",
        "csvFlag": "CsvFlag",
        "pdfFlag": "PdfFlag",
        "xbrlFlag": "XbrlFlag",
    }

    return df.select(mapping.keys()).rename(mapping)


def clean_pdf(content: bytes, doc_id: str) -> pl.DataFrame:
    return pl.DataFrame({"DocumentId": [doc_id], "PdfContent": [content]})


def read_csv(data: bytes) -> pl.DataFrame:
    return pl.read_csv(
        data,
        separator="\t",
        encoding="utf-16-le",
        infer_schema_length=None,
    )


def clean_csv(df: pl.DataFrame, doc_id: str) -> pl.DataFrame:
    return df.select(
        pl.lit(doc_id).alias("DocumentId"),
        pl.all(),
    )
