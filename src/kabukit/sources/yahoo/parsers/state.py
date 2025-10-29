from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, Tag

if TYPE_CHECKING:
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
        return {}  # pragma: no cover

    return json.loads(match.group(1))
