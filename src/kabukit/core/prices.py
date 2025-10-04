from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl

from .base import Base

if TYPE_CHECKING:
    from datetime import timedelta
    from typing import Self

    from polars import Expr

    from .statements import Statements


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

    def with_adjusted_shares(self, statements: Statements) -> Self:
        """日次の調整済み株式数を計算し、列として追加する。

        決算短信で報告される株式数（例：発行済株式総数）は、四半期ごとなど
        特定の日付のデータです。一方で、株式分割や併合は日々発生し、株式数を
        変動させます。
        このメソッドは、直近の決算で報告された株式数を、日々の調整係数
        (`AdjustmentFactor`) を用いて補正し、日次ベースの時系列データとして
        提供します。これにより、日々の時価総額計算などが正確に行えるようになります。

        具体的には、`statements`から`IssuedShares`（発行済株式総数）と
        `TreasuryShares`（自己株式数）を取得し、それぞれを調整します。
        計算結果は、元の列名との混同を避けるため、接頭辞`Adjusted`を付与した
        新しい列（`AdjustedIssuedShares`, `AdjustedTreasuryShares`）として
        追加されます。

        .. note::
            この計算は、決算発表間の株式数の変動が、株式分割・併合
            （`AdjustmentFactor`）にのみ起因すると仮定しています。
            期中に行われる増資や自己株式取得など、`AdjustmentFactor`に
            反映されないイベントによる株式数の変動は考慮されません。

        Args:
            statements (Statements): 財務データを提供する`Statements`オブジェクト。

        Returns:
            Self: `AdjustedIssuedShares`および`AdjustedTreasuryShares`列が
            追加された、新しいPricesオブジェクト。
        """
        shares = statements.number_of_shares().rename({"Date": "ReportDate"})

        adjusted = (
            self.data.join_asof(
                shares,
                left_on="Date",
                right_on="ReportDate",
                by="Code",
                check_sortedness=False,
            )
            .with_columns(
                (1.0 / pl.col("AdjustmentFactor"))
                .cum_prod()
                .over("Code", "ReportDate")
                .alias("CumulativeRatio"),
            )
            .with_columns(
                (pl.col("IssuedShares", "TreasuryShares") * pl.col("CumulativeRatio"))
                .round(0)
                .cast(pl.Int64)
                .name.prefix("Adjusted"),
            )
            .select("Date", "Code", "AdjustedIssuedShares", "AdjustedTreasuryShares")
        )

        data = self.data.join(adjusted, on=["Date", "Code"], how="left")

        return self.__class__(data)

    def with_forecast_profit(self, statements: Statements) -> Self:
        """時系列の予想純利益を列として追加する。

        Args:
            statements (Statements): 財務データを提供する`Statements`オブジェクト。

        Returns:
            Self: `ForecastProfit` 列が追加された、新しいPricesオブジェクト。
        """
        data = self.data.join_asof(
            statements.forecast_profit(),
            on="Date",
            by="Code",
            check_sortedness=False,
        )
        return self.__class__(data)

    def with_forecast_dividend(self, statements: Statements) -> Self:
        """時系列の予想配当総額を列として追加する。

        Args:
            statements (Statements): 財務データを提供する`Statements`オブジェクト。

        Returns:
            Self: `ForecastDividend` 列が追加された、新しいPricesオブジェクト。
        """
        data = self.data.join_asof(
            statements.forecast_dividend(),
            on="Date",
            by="Code",
            check_sortedness=False,
        )
        return self.__class__(data)
