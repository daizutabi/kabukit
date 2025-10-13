from datetime import date, datetime
from zoneinfo import ZoneInfo

import polars as pl
import pytest
from polars import DataFrame


@pytest.fixture(scope="module")
def df() -> DataFrame:
    return DataFrame(
        {
            "csvFlag": ["1", "0"],
            "pdfFlag": ["1", "0"],
            "secCode": ["10000", "20000"],
            "submitDateTime": ["2025-09-19 15:00", "2025-09-22 09:30"],
            "periodStart": ["aa", "2025-09-15"],
            "periodEnd": ["2025-09-30", ""],
            "opeDateTime": ["2025-09-30 15:00", ""],
        },
    )


def test_clean_entries_columns(df: DataFrame) -> None:
    from kabukit.edinet.doc import clean_entries

    df = clean_entries(df, "2025-09-19")
    assert df.columns == [
        "Date",
        "Code",
        "csvFlag",
        "pdfFlag",
        "submitDateTime",
        "periodStart",
        "periodEnd",
        "opeDateTime",
    ]


@pytest.mark.parametrize("d", ["2025-09-19", date(2025, 9, 19)])
def test_clean_entries_date_time(df: DataFrame, d: str | date) -> None:
    from kabukit.edinet.doc import clean_entries

    df = clean_entries(df, d)
    x = df["Date"].to_list()
    assert x[0] == date(2025, 9, 19)
    assert x[1] == date(2025, 9, 19)
    x = df["submitDateTime"].to_list()
    assert x[0] == datetime(2025, 9, 19, 15, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
    assert x[1] == datetime(2025, 9, 22, 9, 30, tzinfo=ZoneInfo("Asia/Tokyo"))


def test_clean_entries_date_time_null() -> None:
    from kabukit.edinet.doc import clean_entries

    df = DataFrame(
        {
            "submitDateTime": ["", None],
            "opeDateTime": ["", ""],
            "secCode": ["10000", "20000"],
        },
    )

    df = clean_entries(df, "2025-09-19")
    assert df["submitDateTime"].to_list() == [None, None]
    assert df["opeDateTime"].dtype == pl.Datetime


def test_clean_entries_flag(df: DataFrame) -> None:
    from kabukit.edinet.doc import clean_entries

    df = clean_entries(df, "2025-09-19")
    assert df["csvFlag"].to_list() == [True, False]
    assert df["pdfFlag"].to_list() == [True, False]


def test_clean_entries_period(df: DataFrame) -> None:
    from kabukit.edinet.doc import clean_entries

    df = clean_entries(df, "2025-09-19")
    assert df["periodStart"].to_list() == [None, date(2025, 9, 15)]
    assert df["periodEnd"].to_list() == [date(2025, 9, 30), None]


def test_clean_entries_ope_datetime(df: DataFrame) -> None:
    from kabukit.edinet.doc import clean_entries

    df = clean_entries(df, "2025-09-19")
    assert df["opeDateTime"].to_list() == [
        datetime(2025, 9, 30, 15, 0, tzinfo=ZoneInfo("Asia/Tokyo")),
        None,
    ]


def test_clean_pdf() -> None:
    from kabukit.edinet.doc import clean_pdf

    df = clean_pdf(b"abc", "abc")
    assert df.columns == ["docID", "pdf"]
    assert df["docID"].to_list() == ["abc"]
    assert df["pdf"].to_list() == [b"abc"]


def test_clean_csv() -> None:
    from kabukit.edinet.doc import clean_csv

    df = DataFrame({"a": [1, 2]})
    df = clean_csv(df, "abc")
    assert df.columns == ["docID", "a"]
    assert df["docID"].to_list() == ["abc", "abc"]
