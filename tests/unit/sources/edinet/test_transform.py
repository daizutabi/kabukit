from __future__ import annotations

import datetime

import polars as pl
import pytest

from kabukit.sources.edinet.columns import ListColumns
from kabukit.sources.edinet.transform import (
    transform_csv,
    transform_list,
    transform_pdf,
)

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "secCode": ["10000", "20000"],
            "submitDateTime": ["2025-09-19 15:00", "2025-09-22 09:30"],
            "filerName": ["a", "b"],
            "docID": ["abc", "def"],
            "docTypeCode": ["1", "2"],
            "docDescription": ["desc1", "desc2"],
            "currentReportReason": ["reason1", "reason2"],
            "periodStart": ["aa", "2025-09-15"],
            "periodEnd": ["2025-09-30", ""],
            "edinetCode": ["E12345", "E67890"],
            "issuerEdinetCode": ["IE12345", "IE67890"],
            "subjectEdinetCode": ["SE12345", "SE67890"],
            "subsidiaryEdinetCode": ["SU12345", "SU67890"],
            "parentDocID": ["pabc", "pdef"],
            "disclosureStatus": ["1", "0"],
            "docInfoEditStatus": ["0", "1"],
            "legalStatus": ["1", "0"],
            "withdrawalStatus": ["0", "1"],
            "attachDocFlag": ["1", "0"],
            "csvFlag": ["1", "0"],
            "pdfFlag": ["1", "0"],
            "xbrlFlag": ["1", "0"],
            "fundCode": [None, None],
        },
    )


def test_transform_list_columns(df: pl.DataFrame) -> None:
    df = transform_list(df, "2025-09-19")
    assert df.columns == [
        "Code",
        "SubmittedDate",
        "SubmittedTime",
        "Company",
        "DocumentId",
        "DocumentTypeCode",
        "DocumentDescription",
        "CurrentReportReason",
        "PeriodStart",
        "PeriodEnd",
        "EdinetCode",
        "IssuerEdinetCode",
        "SubjectEdinetCode",
        "SubsidiaryEdinetCode",
        "ParentDocumentId",
        "DisclosureStatus",
        "DocumentInfoEditStatus",
        "LegalStatus",
        "WithdrawalStatus",
        "AttachDocumentFlag",
        "CsvFlag",
        "PdfFlag",
        "XbrlFlag",
        "FileDate",
    ]


def test_transform_list_submit_date_time(df: pl.DataFrame) -> None:
    df = transform_list(df, "2025-09-19")
    x = df["SubmittedDate"].to_list()
    assert x[0] == datetime.date(2025, 9, 19)
    assert x[1] == datetime.date(2025, 9, 22)
    x = df["SubmittedTime"].to_list()
    assert x[0] == datetime.time(15, 0)
    assert x[1] == datetime.time(9, 30)


def test_transform_list_flag(df: pl.DataFrame) -> None:
    df = transform_list(df, "2025-09-19")
    assert df["CsvFlag"].to_list() == [True, False]
    assert df["PdfFlag"].to_list() == [True, False]


def test_transform_list_period(df: pl.DataFrame) -> None:
    df = transform_list(df, "2025-09-19")
    assert df["PeriodStart"].to_list() == [None, datetime.date(2025, 9, 15)]
    assert df["PeriodEnd"].to_list() == [datetime.date(2025, 9, 30), None]


def test_transform_list_file_date(df: pl.DataFrame) -> None:
    df = transform_list(df, "2025-09-19")
    assert df["FileDate"].unique().to_list() == [datetime.date(2025, 9, 19)]


def test_transform_list_empty() -> None:
    df = pl.DataFrame({"secCode": [None, "1"], "fundCode": ["1", "2"]})
    assert transform_list(df, "2025-09-19").is_empty()


def test_transform_pdf() -> None:
    df = transform_pdf(b"abc", "abc")
    assert df.columns == ["DocumentId", "PdfContent"]
    assert df["DocumentId"].to_list() == ["abc"]
    assert df["PdfContent"].to_list() == [b"abc"]


def test_transform_csv() -> None:
    df = pl.DataFrame({"a": [1, 2]})
    df = transform_csv(df, "abc")
    assert df.columns == ["DocumentId", "a"]
    assert df["DocumentId"].to_list() == ["abc", "abc"]


def test_rename(df: pl.DataFrame) -> None:
    df = transform_list(df, "2025-09-19")
    df = df.select(pl.lit(1).alias("Date"), pl.all())
    df = ListColumns.rename(df, strict=True)
    assert "日付" in df.columns
    assert "銘柄コード" in df.columns
    assert "ファイル日付" in df.columns
