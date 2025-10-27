from __future__ import annotations

import re
from functools import cache
from typing import TYPE_CHECKING

import polars as pl
from bs4 import BeautifulSoup

from kabukit.utils.datetime import strptime

if TYPE_CHECKING:
    import datetime
    from collections.abc import Iterator

    from bs4.element import Tag


@cache
def get_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


PAGER_PATTERN = re.compile(r"pagerLink\('I_list_(\d+)_\d+\.html'\)")


def iter_page_numbers(html: str, /) -> Iterator[int]:
    soup = get_soup(html)
    div = soup.find("div", attrs={"id": "pager-box-top"})

    if div is None:
        return

    for m in PAGER_PATTERN.finditer(str(div)):
        yield int(m.group(1))


def parse_list(html: str, /) -> pl.DataFrame:
    table = get_table(html)

    if table is None:
        return pl.DataFrame()

    data = [dict(iter_cells(tr)) for tr in table.find_all("tr")]
    df = pl.DataFrame(data)

    null_columns = [c for c in df.columns if df[c].dtype == pl.Null]

    return df.with_columns(
        pl.col(null_columns).cast(pl.String),
    )


def get_table(html: str, /) -> Tag | None:
    soup = get_soup(html)
    return soup.find("table", attrs={"id": "main-list-table"})


def iter_cells(tag: Tag, /) -> Iterator[tuple[str, datetime.time | str | None]]:
    tds = tag.find_all("td")

    yield "Code", tds[1].get_text(strip=True)
    yield "DisclosedTime", strptime(tds[0].get_text(strip=True))
    yield "Company", tds[2].get_text(strip=True)
    yield "Title", tds[3].get_text(strip=True)
    yield "PdfLink", get_link(tds[3])
    yield "XbrlLink", get_link(tds[4])
    yield "UpdateStatus", tds[6].get_text(strip=True) or None


def get_link(tag: Tag, /) -> str | None:
    if a := tag.find("a"):
        href = a.get("href")
        if isinstance(href, str):
            return href

    return None
