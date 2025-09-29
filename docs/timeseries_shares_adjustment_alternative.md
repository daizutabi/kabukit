# 日次発行済株式数の調整方法（別解：ハイブリッドアプローチ）

## 概要

`timeseries_shares_adjustment.md` に記載された方法とは別のアプローチで、日々の発行済株式数を計算する方法を記録する。この方法はロジック的に等価であり、どちらを採用するかはコーディングスタイルや好みの問題となる。

このアプローチは、以下の2つのフェーズで構成される。

1.  まず、日々の非累積`AdjustmentFactor`から、全期間を通した「真の累積調整係数」を計算する。
2.  次に、その累積係数に対して、「暗黙的なリセット」ロジック（決算ごとに基準値を再計算する方法）を適用する。

## 計算ロジック

1.  **累積調整係数の作成**:
    `prices_df`上で、日々の`AdjustmentFactor`の逆数の累積積（`cum_prod`）を計算し、全期間を通した`CumulativeFactor`列を作成する。

2.  **基準株式数（BaseShares）の計算**:
    `statements_df`の各決算日に、ステップ1で作成した`CumulativeFactor`を`join_asof`で紐付ける。その後、`ReportedShares / CumulativeFactor` を計算し、正規化された`BaseShares`を求める。

3.  **日次データへの適用**:
    日々の`prices_df`に、ステップ2で計算した`BaseShares`を`join_asof`で紐付ける。

4.  **最終的な株式数の計算**:
    各日に紐付いた`BaseShares`に、その日の`CumulativeFactor`を掛けることで、最終的な`AdjustedNumberOfShares`を算出する。

## 実装コード (polars)

```python
import polars as pl
from datetime import date

# --- 1. サンプルデータの準備 (同じものを使用) ---
statements_df = pl.DataFrame({
    "Date": [date(2023, 3, 31), date(2023, 6, 30), date(2023, 9, 30)],
    "Code": ["A", "A", "A"],
    "NumberOfShares": [1_000_000, 1_100_000, 1_100_000],
})

prices_df = pl.DataFrame({
    "Date": [
        date(2023, 5, 15),
        date(2023, 8, 15), # 分割
        date(2023, 11, 15)
    ],
    "Code": ["A", "A", "A"],
    "AdjustmentFactor": [1.0, 0.5, 1.0],
})

# --- 2. ハイブリッドアプローチによる実装 ---

# ステップ1: 全期間を通した「真の累積調整係数」を作成
prices_with_cumulative_factor = prices_df.with_columns(
    (1.0 / pl.col("AdjustmentFactor")).cum_prod().over("Code").alias("CumulativeFactor")
)

# ステップ2: 決算情報に、その時点の累積係数を紐付け、「BaseShares」を計算
statements_with_base_shares = statements_df.rename(
    {"NumberOfShares": "ReportedShares"}
).join_asof(
    prices_with_cumulative_factor.select(["Date", "Code", "CumulativeFactor"]),
    on="Date",
    by="Code"
).with_columns(
    (pl.col("ReportedShares") / pl.col("CumulativeFactor")).alias("BaseShares")
)

# ステップ3 & 4: 日次データにBaseSharesを紐付け、最終的な株式数を計算
adjusted_df = prices_with_cumulative_factor.join_asof(
    statements_with_base_shares.select(["Date", "Code", "BaseShares"]),
    on="Date",
    by="Code"
).with_columns(
    (pl.col("BaseShares") * pl.col("CumulativeFactor")).round(0).cast(pl.Int64).alias("AdjustedNumberOfShares")
)

print(adjusted_df.select(["Date", "Code", "ReportedShares", "AdjustedNumberOfShares"]))
```
