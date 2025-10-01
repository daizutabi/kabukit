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

    def with_adjusted_shares(
        self,
        statements: Statements,
        target: str | Expr = "TotalShares",
        alias: str | None = None,
    ) -> Self:
        """日次の調整済み株式数を計算し、列として追加する。

        `statements`から指定された株式数（発行済株式総数など）を取得し、
        日々の株式分割・併合（`AdjustmentFactor`）を反映させて調整します。

        Args:
            statements (Statements): 発行済株式数を含むStatementsオブジェクト。
            target (str | Expr, optional):
                調整対象の株式数を指定する。
                文字列ショートカット ("TotalShares", "TreasuryShares",
                "OutstandingShares")
                または polars.Expr が使用可能。デフォルトは "TotalShares"。
            alias (str | None, optional):
                追加される列の名前。指定しない場合、`target`が文字列なら自動生成される。
                `target`がExprの場合は必須。

        Returns:
            Self: 調整済み株式数列が追加された新しいPricesオブジェクト。

        Raises:
            ValueError: サポート外の`target`文字列や、`alias`の指定漏れがあった場合。
        """
        if isinstance(target, str):
            if target == "TotalShares":
                target_expr = pl.col("TotalShares")
            elif target == "TreasuryShares":
                target_expr = pl.col("TreasuryShares")
            elif target == "OutstandingShares":
                target_expr = pl.col("TotalShares") - pl.col("TreasuryShares")
            else:
                msg = f"サポート外のtarget文字列: {target}"
                msg += " 'TotalShares', 'TreasuryShares',"
                msg += " 'OutstandingShares'のいずれか、あるいはpolars.Exprを使用する。"
                raise ValueError(msg)
        else:
            target_expr = target

        if alias is None:
            if isinstance(target, str):
                output_col_name = f"Adjusted{target}"
            else:
                msg = "`alias`は、polars.Exprを`target`に指定した場合には必須です。"
                raise ValueError(msg)
        else:
            output_col_name = alias

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
            .select(
                "Date",
                "Code",
                (target_expr * pl.col("CumulativeRatio"))
                .round(0)
                .cast(pl.Int64)
                .alias(output_col_name),
            )
        )

        data = self.data.join(adjusted, on=["Date", "Code"], how="left")

        return self.__class__(data)
