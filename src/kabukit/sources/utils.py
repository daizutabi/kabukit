from __future__ import annotations

import io
import zipfile
from functools import cache
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

if TYPE_CHECKING:
    import re


@cache
def get_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def extract_content(content: bytes, pattern: re.Pattern[str]) -> bytes | None:
    buffer = io.BytesIO(content)

    with zipfile.ZipFile(buffer) as zf:
        for info in zf.infolist():
            if pattern.match(info.filename):
                with zf.open(info) as f:
                    return f.read()

    return None
