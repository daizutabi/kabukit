import asyncio
import sys
from pathlib import Path

import polars as pl
from polars import col as c

# プロジェクトのルートディレクトリをパスに追加してkabukitモジュールをインポート
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from kabukit.core.prices import Prices
from kabukit.core.statements import Statements
from kabukit.jquants.concurrent import fetch


async def main():
    """
    StatementsのNumberOfSharesとPricesのRelativeSharesの乖離を調査する。
    """
    print("分析を開始します...")

    # --- 1. データの準備 ---
    print("データを読み込んでいます...")
    # テストで使った、分割履歴のある銘柄リストを使用
    codes = ["33500", "62000", "33990", "71870", "65420", "38160", "49230"]

    # Statementsはキャッシュから読み込む
    try:
        statements = Statements.read()
        stmt_df = statements.data.filter(c.Code.is_in(codes)).select(
            "Code",
            "Date",
            "TypeOfDocument",
            "NumberOfShares",
        )
    except FileNotFoundError:
        print("Statementsのキャッシュデータが見つかりません。スクリプトを終了します。")
        return

    # PricesはAPIから最新を取得
    prices_df = Prices(await fetch("prices", codes)).with_relative_shares().data
    print("データの準備が完了しました。")

    # --- 2. 乖離の計算 ---
    print("乖離を計算しています...")
    # 決算日に対応するRelativeSharesを紐付ける (as-of join)
    merged_df = (
        stmt_df.drop_nulls("NumberOfShares")
        .sort("Date")
        .join_asof(prices_df.sort("Date"), on="Date", by="Code")
    )

    # 1期間前の値を取得
    merged_with_prev_df = merged_df.with_columns(
        [
            pl.col("NumberOfShares").shift(1).over("Code").alias("PrevNumberOfShares"),
            pl.col("RelativeShares").shift(1).over("Code").alias("PrevRelativeShares"),
        ],
    ).drop_nulls()

    # 3. 予測値と実績値を計算
    analysis_df = merged_with_prev_df.with_columns(
        (
            pl.col("PrevNumberOfShares")
            * (pl.col("RelativeShares") / pl.col("PrevRelativeShares"))
        ).alias("PredictedNumberOfShares"),
    )

    # 4. 乖離（相対誤差）を計算
    final_df = analysis_df.with_columns(
        (
            (pl.col("NumberOfShares") - pl.col("PredictedNumberOfShares")).abs()
            / (pl.col("NumberOfShares") + 1e-9)
        ).alias("RelativeError"),
    ).sort("RelativeError", descending=True)

    print("計算が完了しました。")
    print("-" * 80)
    print("「実績株数」と「予測株数」の乖離が大きい上位20件:")
    print(
        final_df.select(
            [
                "Code",
                "Date",
                "TypeOfDocument",
                "NumberOfShares",
                "PredictedNumberOfShares",
                "RelativeError",
            ],
        ).head(20),
    )
    print("-" * 80)


if __name__ == "__main__":
    asyncio.run(main())
