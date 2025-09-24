from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl
from platformdirs import user_cache_dir

if TYPE_CHECKING:
    from typing import Self

    from polars import DataFrame


class Base:
    data: DataFrame

    def __init__(self, data: DataFrame) -> None:
        self.data = data

    @classmethod
    def data_dir(cls) -> Path:
        clsname = cls.__name__.lower()
        return Path(user_cache_dir("kabukit")) / clsname

    def write(self) -> Path:
        data_dir = self.data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        path = datetime.datetime.today().strftime("%Y%m%d")  # noqa: DTZ002
        filename = data_dir / f"{path}.parquet"
        self.data.write_parquet(filename)
        return filename

    @classmethod
    def read(cls, path: str | None = None) -> Self:
        data_dir = cls.data_dir()

        if path is None:
            filename = sorted(data_dir.glob("*.parquet"))[-1]
        else:
            filename = data_dir / path

        data = pl.read_parquet(filename)
        return cls(data)
