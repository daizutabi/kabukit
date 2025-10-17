from __future__ import annotations

from typing import TYPE_CHECKING

from kabukit.utils.config import get_cache_dir

from . import cache

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path
    from typing import Any, Self

    from polars import DataFrame
    from polars._typing import IntoExprColumn


class Base:
    data: DataFrame

    def __init__(
        self,
        data: DataFrame | None = None,
        *,
        path: str | Path | None = None,
    ) -> None:
        if data is not None:
            self.data = data
            return

        self.data = cache.read(self.__class__.__name__.lower(), path)

    @classmethod
    def data_dir(cls) -> Path:
        clsname = cls.__name__.lower()
        return get_cache_dir() / clsname

    def write(self) -> Path:
        return cache.write(self.__class__.__name__.lower(), self.data)

    def filter(
        self,
        *predicates: IntoExprColumn | Iterable[IntoExprColumn] | bool | list[bool],
        **constraints: Any,
    ) -> Self:
        """Filter the data with given predicates and constraints."""
        data = self.data.filter(*predicates, **constraints)
        return self.__class__(data)
