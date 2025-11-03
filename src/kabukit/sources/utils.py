from __future__ import annotations

from functools import cache

from bs4 import BeautifulSoup


@cache
def get_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")
