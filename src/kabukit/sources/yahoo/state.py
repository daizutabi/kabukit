from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

import polars as pl
from bs4 import BeautifulSoup, Tag

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any

PRELOADED_STATE_PATTERN = re.compile(r"window\.__PRELOADED_STATE__\s*=\s*(\{.*\})")


def get_preloaded_state(text: str) -> dict[str, Any]:
    """HTMLテキストから `__PRELOADED_STATE__` を抽出して辞書として返す。

    Args:
        text: HTMLテキスト。

    Returns:
        抽出した状態辞書。見つからなかった場合は空の辞書。
    """
    soup = BeautifulSoup(text, "lxml")
    script = soup.find("script", string=PRELOADED_STATE_PATTERN)  # pyright: ignore[reportCallIssue, reportArgumentType, reportUnknownVariableType], # ty: ignore[no-matching-overload]

    if not isinstance(script, Tag):
        return {}

    match = PRELOADED_STATE_PATTERN.search(script.text)

    if match is None:
        return {}

    return json.loads(match.group(1))


def parse(text: str, code: str) -> pl.DataFrame:
    state = get_preloaded_state(text)

    if not state:
        return pl.DataFrame()

    return pl.DataFrame({"Code": [code], "text": [text]})


def iter_values(
    state: dict[str, Any],
    prefix: str = "",
) -> Iterator[tuple[str, Any]]:
    """状態辞書のすべての値を再帰的に反復処理するジェネレーター。

    Args:
        state (dict[str, Any]): 状態辞書。

    Yields:
        辞書内のすべての値。
    """
    for key, value in state.items():
        if isinstance(value, dict):
            yield from iter_values(value, f"{prefix}{key}.")  # pyright: ignore[reportUnknownArgumentType]
        else:
            yield f"{prefix}{key}", value
