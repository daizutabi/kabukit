from __future__ import annotations

import re
from typing import TYPE_CHECKING

from kabukit.sources.utils import get_soup

if TYPE_CHECKING:
    from collections.abc import Iterator


def iter_shares_urls(text: str) -> Iterator[str]:
    soup = get_soup(text)
    select = soup.find("select", class_="backnumber")

    if select is None:
        return

    for option in select.find_all("option"):
        value = option.get("value")
        if isinstance(value, str):
            yield value


def iter_shares_links(text: str) -> Iterator[str]:
    soup = get_soup(text)

    pattern = re.compile(r"HP-\d{4}\.\d{1,2}\.pdf")

    for a in soup.find_all("a", href=pattern):
        href = a.get("href")
        if isinstance(href, str):
            yield href
