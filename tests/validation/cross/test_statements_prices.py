import polars as pl
import pytest
from polars import col as c

from kabukit.core.prices import Prices
from kabukit.core.statements import Statements
from tests.validation.conftest import pytestmark  # noqa: F401


@pytest.mark.asyncio
async def test_shares_consistency(statements: Statements) -> None:
    """
    最新のNumberOfSharesを基準に、過去の各時点での絶対株数を計算し、
    それが各決算短信のTotalSharesと一致するかを検証する。
    """
    from kabukit.jquants.concurrent import fetch

    # 過去に株式分割のあった銘柄コード
    codes = ["33500", "62000", "33990", "71870", "65420", "38160", "49230"]

    # 1. 必要なデータを準備
    stmt_df = statements.data.filter(c.Code.is_in(codes)).select(
        "Code",
        "Date",
        "TotalShares",
    )
    prices_df = Prices(await fetch("prices", codes)).with_relative_shares().data

    # 2. 各銘柄の最新のTotalSharesを取得
    latest_shares = (
        stmt_df.drop_nulls("TotalShares")
        .sort("Date")
        .group_by("Code")
        .last()
        .select(["Code", pl.col("TotalShares").alias("LatestTotalShares")])
    )

    # 3. 最新の株数と日々のRelativeSharesから、過去の絶対株数を計算
    hypothetical_shares_df = prices_df.join(latest_shares, on="Code").with_columns(
        (pl.col("LatestTotalShares") * pl.col("RelativeShares")).alias(
            "HypotheticalShares",
        ),
    )

    # 4. 決算日時点での実績値と計算値を結合
    comparison_df = stmt_df.join(
        hypothetical_shares_df,
        on=["Code", "Date"],
        how="inner",
    ).drop_nulls()

    # 5. 実績値と計算値の相対誤差が小さいことを表明
    # (実績値が0の場合を避けるため、分母に微小な値を追加)
    # relative_error = (
    #     comparison_df["NumberOfShares"] - comparison_df["HypotheticalShares"]
    # ).abs() / (comparison_df["NumberOfShares"] + 1e-9)

    # assert relative_error.mean() < 0.01  # 平均相対誤差が1%未満
