from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl

from .base import Base

if TYPE_CHECKING:
    from polars import DataFrame


class Statements(Base):
    def number_of_shares(self) -> DataFrame:
        """発行済株式数を取得する。"""
        return self.data.filter(
            pl.col("TotalShares").is_not_null(),
        ).select(
            "Date",
            "Code",
            "TotalShares",
            "TreasuryShares",
            "AverageOutstandingShares",
        )
