from __future__ import annotations

import datetime

import polars as pl
import pytest
from bs4 import BeautifulSoup
from polars.testing import assert_frame_equal

from kabukit.sources.tdnet.parser import (
    get_link,
    get_table,
    iter_cells,
    iter_dates,
    iter_page_numbers,
    parse_list,
)
from kabukit.sources.utils import get_soup

pytestmark = pytest.mark.unit


def test_iter_dates() -> None:
    html = """
    <select name="daylist">
        <option value="I_list_001_20230101.html">2023/01/01</option>
        <option value="I_list_001_20230102.html">2023/01/02</option>
    </select>
    """
    result = list(iter_dates(html))
    expected = [datetime.date(2023, 1, 1), datetime.date(2023, 1, 2)]
    assert result == expected


def test_iter_dates_no_daylist() -> None:
    html = """
    <select>
        <option value="I_list_001_20230101.html">2023/01/01</option>
        <option value="I_list_001_20230102.html">2023/01/02</option>
    </select>
    """
    assert list(iter_dates(html)) == []


FAKE_HTML_WITH_PAGER = """
<html>
<body>
    <div id="pager-box-top">
        <a href="#" onclick="pagerLink('I_list_001_20230101.html')">1</a>
        <a href="#" onclick="pagerLink('I_list_002_20230101.html')">2</a>
        <a href="#" onclick="pagerLink('I_list_003_20230101.html')">3</a>
    </div>
</body>
</html>
"""

FAKE_HTML_WITHOUT_PAGER = "<html><body></body></html>"

FAKE_HTML_WITH_TABLE = """
<html>
<body>
<table id="main-list-table">
    <tr>
        <td>10:00</td>
        <td>1301</td>
        <td>極洋</td>
        <td><a href="some/path.pdf">自己株式の取得結果</a></td>
        <td><a href="some/xbrl.zip">XBRL</a></td>
        <td>東証</td>
        <td></td>
    </tr>
    <tr>
        <td>11:00</td>
        <td>1302</td>
        <td>日清製粉</td>
        <td><a href="other/path.pdf">役員人事</a></td>
        <td></td>
        <td>東証</td>
        <td>更新</td>
    </tr>
</table>
</body>
</html>
"""

FAKE_HTML_WITHOUT_TABLE = "<html><body></body></html>"


def test_get_soup_cache() -> None:
    html = "<html><body><p>hello</p></body></html>"
    soup1 = get_soup(html)
    soup2 = get_soup(html)
    assert soup1 is soup2
    assert isinstance(soup1, BeautifulSoup)


def test_iter_page_numbers() -> None:
    result = list(iter_page_numbers(FAKE_HTML_WITH_PAGER))
    assert result == [1, 2, 3]


def test_iter_page_numbers_no_pager() -> None:
    result = list(iter_page_numbers(FAKE_HTML_WITHOUT_PAGER))
    assert result == []


def test_get_table() -> None:
    table = get_table(FAKE_HTML_WITH_TABLE)
    assert table is not None
    assert table.name == "table"


def test_get_table_no_table() -> None:
    table = get_table(FAKE_HTML_WITHOUT_TABLE)
    assert table is None


def test_parse_list() -> None:
    df = parse_list(FAKE_HTML_WITH_TABLE)
    expected = pl.DataFrame(
        {
            "Code": ["1301", "1302"],
            "DisclosedTime": [datetime.time(10, 0), datetime.time(11, 0)],
            "Company": ["極洋", "日清製粉"],
            "Title": ["自己株式の取得結果", "役員人事"],
            "PdfLink": ["some/path.pdf", "other/path.pdf"],
            "XbrlLink": ["some/xbrl.zip", None],
            "UpdateStatus": [None, "更新"],
        },
    )
    assert_frame_equal(df, expected)


def test_parse_list_no_table() -> None:
    df = parse_list(FAKE_HTML_WITHOUT_TABLE)
    assert df.is_empty()


def test_iter_cells() -> None:
    soup = BeautifulSoup(FAKE_HTML_WITH_TABLE, "lxml")
    tr = soup.find("tr")
    assert tr is not None
    result = dict(iter_cells(tr))
    expected = {
        "Code": "1301",
        "DisclosedTime": datetime.time(10, 0),
        "Company": "極洋",
        "Title": "自己株式の取得結果",
        "PdfLink": "some/path.pdf",
        "XbrlLink": "some/xbrl.zip",
        "UpdateStatus": None,
    }
    assert result == expected


def test_get_link() -> None:
    soup = BeautifulSoup('<td><a href="test.pdf">link</a></td>', "lxml")
    td = soup.find("td")
    assert td is not None
    assert get_link(td) == "test.pdf"


def test_get_link_no_link() -> None:
    soup = BeautifulSoup("<td>no link</td>", "lxml")
    td = soup.find("td")
    assert td is not None
    assert get_link(td) is None
