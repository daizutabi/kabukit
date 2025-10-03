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
            pl.col("IssuedShares").is_not_null(),
        ).select(
            "Date",
            "Code",
            "IssuedShares",
            "TreasuryShares",
            "AverageOutstandingShares",
        )

    def forecast_profit(self) -> DataFrame:
        """予想純利益を抽出する。

        Returns:
            DataFrame: Date, Code, ForecastProfit を含むDataFrame
        """
        return (
            self.data.with_columns(
                pl.when(pl.col("TypeOfCurrentPeriod").str.starts_with("FY"))
                .then(pl.col("NextYearForecastProfit"))
                .otherwise(pl.col("ForecastProfit"))
                .alias("ForecastProfit"),
            )
            .filter(pl.col("ForecastProfit").is_not_null())
            .select("Date", "Code", "ForecastProfit")
        )
