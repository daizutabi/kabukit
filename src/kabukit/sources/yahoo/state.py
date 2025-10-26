from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any


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
