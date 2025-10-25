from __future__ import annotations

import datetime

import polars as pl
import pytest

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


def test_clean_list_columns(df: pl.DataFrame) -> None:
    from kabukit.sources.edinet.document import clean_list

    df = clean_list(df)
    assert df.columns == [
        "Code",
        "SubmitDate",
        "SubmitTime",
        "CompanyName",
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
    ]


def test_clean_list_submit_date_time(df: pl.DataFrame) -> None:
    from kabukit.sources.edinet.document import clean_list

    df = clean_list(df)
    x = df["SubmitDate"].to_list()
    assert x[0] == datetime.date(2025, 9, 19)
    assert x[1] == datetime.date(2025, 9, 22)
    x = df["SubmitTime"].to_list()
    assert x[0] == datetime.time(15, 0)
    assert x[1] == datetime.time(9, 30)


def test_clean_list_flag(df: pl.DataFrame) -> None:
    from kabukit.sources.edinet.document import clean_list

    df = clean_list(df)
    assert df["CsvFlag"].to_list() == [True, False]
    assert df["PdfFlag"].to_list() == [True, False]


def test_clean_list_period(df: pl.DataFrame) -> None:
    from kabukit.sources.edinet.document import clean_list

    df = clean_list(df)
    assert df["PeriodStart"].to_list() == [None, datetime.date(2025, 9, 15)]
    assert df["PeriodEnd"].to_list() == [datetime.date(2025, 9, 30), None]


def test_clean_list_empty() -> None:
    from kabukit.sources.edinet.document import clean_list

    df = pl.DataFrame({"secCode": [None, "1"], "fundCode": ["1", "2"]})
    assert clean_list(df).is_empty()


def test_clean_pdf() -> None:
    from kabukit.sources.edinet.document import clean_pdf

    df = clean_pdf(b"abc", "abc")
    assert df.columns == ["docID", "pdf"]
    assert df["docID"].to_list() == ["abc"]
    assert df["pdf"].to_list() == [b"abc"]


def test_read_csv() -> None:
    from kabukit.sources.edinet.document import read_csv

    data = "col1\tcol2\n1\t2\n3\t4".encode("utf-16-le")
    df = read_csv(data)
    assert df.columns == ["col1", "col2"]
    assert df["col1"].to_list() == [1, 3]
    assert df["col2"].to_list() == [2, 4]


def test_clean_csv() -> None:
    from kabukit.sources.edinet.document import clean_csv

    df = pl.DataFrame({"a": [1, 2]})
    df = clean_csv(df, "abc")
    assert df.columns == ["docID", "a"]
    assert df["docID"].to_list() == ["abc", "abc"]


def test_renamest(df: pl.DataFrame) -> None:
    from kabukit.sources.edinet.columns import ListColumns
    from kabukit.sources.edinet.document import clean_list

    df = clean_list(df)
    df = df.select(pl.lit(1).alias("Date"), pl.all())
    df = ListColumns.rename(df, strict=True)
    assert "日付" in df.columns
    assert "銘柄コード" in df.columns
