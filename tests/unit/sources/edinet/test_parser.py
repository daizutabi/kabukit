from __future__ import annotations

import io
import zipfile

import pytest

from kabukit.sources.edinet.parser import parse_csv, parse_pdf, read_csv

pytestmark = pytest.mark.unit


def test_read_csv() -> None:
    data = "col1\tcol2\n1\t2\n3\t4".encode("utf-16-le")
    df = read_csv(data)
    assert df.columns == ["col1", "col2"]
    assert df["col1"].to_list() == [1, 3]
    assert df["col2"].to_list() == [2, 4]


def test_parse_pdf() -> None:
    df = parse_pdf(b"abc", "abc")
    assert df.columns == ["DocumentId", "PdfContent"]
    assert df["DocumentId"].to_list() == ["abc"]
    assert df["PdfContent"].to_list() == [b"abc"]


def test_parse_csv() -> None:
    csv_content = "header1\theader2\nvalue1\tvalue2\nvalue3\tvalue4"
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("a/b/test.csv", csv_content.encode("utf-16-le"))
    content = zip_buffer.getvalue()

    df = parse_csv(content, "abc")
    assert df.columns == ["DocumentId", "header1", "header2"]
    assert df["DocumentId"].to_list() == ["abc", "abc"]
