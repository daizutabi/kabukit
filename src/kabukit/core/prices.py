from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl

from .base import Base

if TYPE_CHECKING:
    from datetime import timedelta
    from typing import Self

    from polars import Expr


class Prices(Base):
    def truncate(self, every: str | timedelta | Expr) -> Self:
        data = (
            self.data.group_by(pl.col("Date").dt.truncate(every), "Code")
            .agg(
                pl.col("Open").drop_nulls().first(),
                pl.col("High").max(),
                pl.col("Low").min(),
                pl.col("Close").drop_nulls().last(),
                pl.col("Volume").sum(),
                pl.col("TurnoverValue").sum(),
            )
            .sort("Code", "Date")
        )
        return self.__class__(data)
