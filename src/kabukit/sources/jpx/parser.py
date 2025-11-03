from __future__ import annotations

import calendar
import datetime
import io
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

import polars as pl
from pypdf import PdfReader

from kabukit.sources.utils import get_soup

if TYPE_CHECKING:
    from collections.abc import Iterator


def iter_shares_urls(html: str, /) -> Iterator[str]:
    soup = get_soup(html)
    select = soup.find("select", class_="backnumber")

    if select is None:
        return

    for option in select.find_all("option"):
        value = option.get("value")
        if isinstance(value, str):
            yield value


def iter_shares_links(html: str, /) -> Iterator[str]:
    soup = get_soup(html)

    pattern = re.compile(r"HP-\d{4}\.\d{1,2}\.pdf")

    for a in soup.find_all("a", href=pattern):
        href = a.get("href")
        if isinstance(href, str):
            yield href


@dataclass
class Shares:
    name: str
    code: str
    number: int
    year: int
    month: int

    def to_dict(self) -> dict[str, str | int | datetime.date]:
        day = calendar.monthrange(self.year, self.month)[1]
        date = datetime.date(self.year, self.month, day)

        return {
            "Date": date,
            "Code": self.code,
            "Company": self.name,
            "IssuedShares": self.number,
        }


def iter_shares_pages(content: bytes, /) -> Iterator[str]:
    reader = PdfReader(io.BytesIO(content))

    header = r"^\s*\d{4}年\d{1,2}月分.+会社別\n会社名\s+（コード）\s+月末現在上場株式数"
    pattern = re.compile(header, re.DOTALL)
    in_shares = False

    for page in reader.pages:
        text = page.extract_text()
        if in_shares:
            yield text
        elif pattern.match(text):
            in_shares = True
            yield text


def iter_shares(page: str, /) -> Iterator[Shares]:
    m = re.match(r"^\s*(\d{4})年(\d{1,2})月分\n", page)
    if not m:
        return

    year, month = map(int, m.groups())

    pattern = re.compile(r"^(.+)\s+\(([0-9A-Z]{4})\)\s([\d,]+)\s+")

    for line in page.splitlines():
        m = pattern.match(line)
        if m:
            name, code, number = m.groups()
            number = int(number.replace(",", ""))
            yield Shares(name, code, number, year, month)


def parse_shares(content: bytes, /) -> pl.DataFrame:
    pages = iter_shares_pages(content)
    shares = (share.to_dict() for page in pages for share in iter_shares(page))
    return pl.DataFrame(shares)
