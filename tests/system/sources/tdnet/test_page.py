from __future__ import annotations

import re

from bs4.element import Tag


def test_page_pager_box_top(page: str) -> None:
    assert 'id="pager-box-top"' in page


def test_iter_page_numbers(page: str) -> None:
    from kabukit.sources.tdnet.page import iter_page_numbers

    pages = list(iter_page_numbers(page))
    assert 1 in pages
    assert sorted(set(pages)) == pages


def test_table_format(table: Tag) -> None:  # noqa: C901
    for row in table.find_all("tr"):
        for k, td in enumerate(row.find_all("td")):
            if k == 0:  # 時刻
                assert re.match(r"\d\d:\d\d", td.get_text())
            elif k == 1:  # コード
                assert len(td.get_text()) == 5
            elif k == 2:  # 会社名
                assert td.get_text(strip=True)
            elif k == 3:  # 表題
                title = td.get_text(strip=True)
                assert title
                a = td.find("a")
                assert isinstance(a, Tag)
                href = a.get("href")
                assert isinstance(href, str)
                assert href.endswith(".pdf")
            elif k == 4:  # XBRL
                if a := td.find("a"):
                    href = a.get("href")
                    assert isinstance(href, str)
                    assert href.endswith(".zip")
            elif k == 5:  # 上場取引所
                assert td.get_text(strip=True)
            elif k == 6:  # 更新履歴
                assert td.get_text(strip=True) or True
