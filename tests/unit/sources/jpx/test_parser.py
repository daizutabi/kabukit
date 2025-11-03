from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from kabukit.sources.jpx.parser import (
    Shares,
    iter_shares,
    iter_shares_links,
    iter_shares_pages,
    iter_shares_urls,
    parse_shares,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


FAKE_HTML_URLS = """
<html>
<body>
    <select class="backnumber">
        <option value="https://example.com/a.html">A</option>
        <option value="https://example.com/b.html">B</option>
    </select>
</body>
</html>
"""

FAKE_HTML_URLS_NO_SELECT = "<html><body></body></html>"

FAKE_HTML_LINKS = """
<html>
<body>
    <a href="https://example.com/HP-2023.10.pdf">PDF1</a>
    <a href="https://example.com/HP-2023.9.pdf">PDF2</a>
    <a href="https://example.com/other.pdf">Other</a>
</body>
</html>
"""

FAKE_HTML_LINKS_NO_MATCH = """
<html><body><a href="other.pdf">Other</a></body></html>
"""


def test_iter_shares_urls() -> None:
    urls = list(iter_shares_urls(FAKE_HTML_URLS))
    assert urls == ["https://example.com/a.html", "https://example.com/b.html"]


def test_iter_shares_urls_no_select() -> None:
    urls = list(iter_shares_urls(FAKE_HTML_URLS_NO_SELECT))
    assert not urls


def test_iter_shares_links() -> None:
    links = list(iter_shares_links(FAKE_HTML_LINKS))
    assert links == [
        "https://example.com/HP-2023.10.pdf",
        "https://example.com/HP-2023.9.pdf",
    ]


def test_iter_shares_links_no_match() -> None:
    links = list(iter_shares_links(FAKE_HTML_LINKS_NO_MATCH))
    assert not links


def test_shares_to_dict() -> None:
    share = Shares(company="Test", code="1234", number=100, year=2023, month=10)
    expected = {
        "Date": datetime.date(2023, 10, 31),
        "Code": "1234",
        "Company": "Test",
        "IssuedShares": 100,
    }
    assert share.to_dict() == expected


def test_iter_shares_pages(mocker: MockerFixture) -> None:
    mock_reader = mocker.MagicMock()

    mock_page0 = mocker.MagicMock()
    mock_page0.extract_text.return_value = "Irrelevant text"

    mock_page1 = mocker.MagicMock()
    page1_text = "2023年10月分　会社別\n会社名 （コード） 月末現在上場株式数\n..."
    mock_page1.extract_text.return_value = page1_text

    mock_page2 = mocker.MagicMock()
    page2_text = "Page 2 text"
    mock_page2.extract_text.return_value = page2_text

    mock_reader.pages = [mock_page0, mock_page1, mock_page2]
    mocker.patch("kabukit.sources.jpx.parser.PdfReader", return_value=mock_reader)

    pages_text = list(iter_shares_pages(b"dummy pdf content"))

    assert pages_text == [page1_text, page2_text]


def test_iter_shares_pages_no_match(mocker: MockerFixture) -> None:
    mock_reader = mocker.MagicMock()
    mock_page = mocker.MagicMock()
    mock_page.extract_text.return_value = "Irrelevant text"
    mock_reader.pages = [mock_page]
    mocker.patch("kabukit.sources.jpx.parser.PdfReader", return_value=mock_reader)

    pages_text = list(iter_shares_pages(b"dummy pdf content"))
    assert not pages_text


def test_iter_shares() -> None:
    page_text = """
2023年10月分
会社名 （コード） 月末現在上場株式数
Ａ社 (123A) 1,000,000
Ｂ社 (456B) 2,000,000
"""
    shares = list(iter_shares(page_text))
    assert len(shares) == 2

    s1 = shares[0]
    assert s1.company == "Ａ社"
    assert s1.code == "123A"
    assert s1.number == 1000000
    assert s1.year == 2023
    assert s1.month == 10

    s2 = shares[1]
    assert s2.company == "Ｂ社"
    assert s2.code == "456B"
    assert s2.number == 2000000


def test_iter_shares_no_header() -> None:
    page_text = "Ａ社 (123A) 1,000,000"
    shares = list(iter_shares(page_text))
    assert not shares


def test_parse_shares(mocker: MockerFixture) -> None:
    page1_text = """
2023年10月分
Ａ社 (123A) 1,000,000
Ｂ社 (456B) 2,000,000
"""
    page2_text = """
2023年11月分
Ｃ社 (789C) 3,000,000
"""
    mocker.patch(
        "kabukit.sources.jpx.parser.iter_shares_pages",
        return_value=iter([page1_text, page2_text]),
    )

    df = parse_shares(b"fake content")

    expected = pl.DataFrame(
        {
            "Date": [
                datetime.date(2023, 10, 31),
                datetime.date(2023, 10, 31),
                datetime.date(2023, 11, 30),
            ],
            "Code": ["123A", "456B", "789C"],
            "Company": ["Ａ社", "Ｂ社", "Ｃ社"],
            "IssuedShares": [1000000, 2000000, 3000000],
        },
    )
    assert_frame_equal(df, expected)


def test_parse_shares_empty(mocker: MockerFixture) -> None:
    mocker.patch(
        "kabukit.sources.jpx.parser.iter_shares_pages",
        return_value=iter([]),
    )
    df = parse_shares(b"fake content")
    assert df.is_empty()
