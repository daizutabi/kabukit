from __future__ import annotations

import io
import zipfile
from functools import cache
from typing import TYPE_CHECKING, Literal, overload

import polars as pl
from bs4 import BeautifulSoup

if TYPE_CHECKING:
    import re
    from collections.abc import Iterator


def normalize_code(data: pl.DataFrame, /, column: str = "Code") -> pl.DataFrame:
    """証券コードを４桁の形式に正規化する。

    Args:
        data (pl.DataFrame): 正規化前の証券コードを含むDataFrame。
        column (str): 正規化する列名。デフォルトは"Code"。

    Returns:
        pl.DataFrame: 正規化された証券コードを含むDataFrame。
    """
    return data.filter(
        pl.col(column).str.len_chars() == 5,
        pl.col(column).str.ends_with("0"),
    ).with_columns(
        pl.col(column).str.slice(0, 4),
    )


@cache
def get_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


@overload
def iter_contents(
    content: bytes,
    pattern: re.Pattern[str],
    *,
    include_filename: Literal[False] = False,
) -> Iterator[bytes]: ...


@overload
def iter_contents(
    content: bytes,
    pattern: re.Pattern[str],
    *,
    include_filename: Literal[True],
) -> Iterator[tuple[str, bytes]]: ...


def iter_contents(
    content: bytes,
    pattern: re.Pattern[str],
    *,
    include_filename: bool = False,
) -> Iterator[bytes] | Iterator[tuple[str, bytes]]:
    buffer = io.BytesIO(content)

    with zipfile.ZipFile(buffer) as zf:
        for info in zf.infolist():
            if pattern.match(info.filename):
                with zf.open(info) as f:
                    if include_filename:
                        yield info.filename, f.read()
                    else:
                        yield f.read()
