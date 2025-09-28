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

    def with_relative_shares(self) -> Self:
        """株式分割・併合を考慮した相対的な株式数を計算し、`RelativeShares`列を追加する。

        `AdjustmentFactor`の累積積を逆順で計算することにより、
        最新の株式数を1とした場合の、過去の相対的な株式数を算出する。
        例えば、2:1の株式分割があった場合、分割以前の`RelativeShares`は0.5になる。

        Returns:
            Prices: `RelativeShares`列が追加された新しいPricesオブジェクト。
        """
        # この処理は、各銘柄コード内で日付が昇順にソートされていることを前提とします
        df = self.data.with_columns(
            pl.col("AdjustmentFactor")
            .shift(-1)
            .fill_null(1.0)
            .reverse()
            .cum_prod()
            .reverse()
            .over("Code")
            .alias("RelativeShares"),
        )
        return self.__class__(df)
