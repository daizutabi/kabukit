# 日次株価データに対する発行済株式数の調整方法

## 概要

四半期ごとにしか発表されない発行済株式数を、日々の株価データに追従させ、株式分割・併合の影響を正しく反映させるための`polars`を使った実装方法を記録する。

## 前提条件

以下の2つのデータフレームが存在することを前提とする。

1.  **決算短信データ (`statements_df`)**
    *   **カラム**: `Date`, `Code`, `NumberOfShares`
    *   **特徴**: データは四半期ごとなど、疎な日付で存在する。`NumberOfShares`は、その決算期末時点での発行済株式総数。

2.  **株価データ (`prices_df`)**
    *   **カラム**: `Date`, `Code`, `AdjustmentFactor`
    *   **特徴**: データは営業日毎日存在する。`AdjustmentFactor`は**非累積**であり、株式分割や併合の**権利落ち日にのみ**その比率に応じた数値（例: 1:2分割なら0.5）が記録され、それ以外の日は`1.0`となる。

## 計算ロジック（最終版）

1.  **日次データへの決算情報紐付け**:
    まず、日次の`prices_df`に、`statements_df`を`join_asof`で結合する。この際、決算日を後でグループ化のキーとして使うため、`statements_df`の`Date`列を`ReportDate`などにリネームしておく。これにより、各日に、その日以前の最新の決算日(`ReportDate`)と発行済株式数(`ReportedShares`)が紐付く。

2.  **計算期間のグループ化**:
    **決算日の変わり目**を基準に、計算をリセットするためのグループ（`period_id`）を作成する。キーとして`ReportDate`の変わり目を使うことで、連続する決算で`ReportedShares`の値が同じだったとしても、必ず新しいグループが作成され、計算が正しくリセットされる。

3.  **日々の株式数変動率の計算**:
    `AdjustmentFactor`は株価に乗算するものなので、株式数に対してはその逆数を適用する。その日の株式数の変動率は `1.0 / AdjustmentFactor` となる。（例: 2分割でFactorが0.5なら、変動率は2.0倍）

4.  **累積変動率の計算**:
    ステップ2で作成した`period_id`のグループ内で、日々の株式数変動率の**累積積 (`cum_prod`)** を計算する。これにより、決算日を起点とした、その日までの累積の分割・併合倍率（`CumulativeRatio`）が求まる。

5.  **最終的な株式数の計算**:
    各日の`ReportedShares`に、ステップ4で計算した`CumulativeRatio`を掛けることで、その日の正しい`AdjustedNumberOfShares`が求まる。
    ```
    AdjustedNumberOfShares = ReportedShares * CumulativeRatio
    ```

## 実装コード (polars) - 修正版

```python
import polars as pl
from datetime import date

# --- 1. サンプルデータの準備 ---
# 6/30と9/30の決算で株式数が同じ、というエッジケースを再現
statements_df = pl.DataFrame({
    "Date": [date(2023, 3, 31), date(2023, 6, 30), date(2023, 9, 30)],
    "Code": ["A", "A", "A"],
    "NumberOfShares": [1_000_000, 1_100_000, 1_100_000],
})

# 8/15に分割が発生するシナリオ
prices_df = pl.DataFrame({
    "Date": [
        date(2023, 5, 15), # 3/31決算の期間
        date(2023, 8, 15), # 6/30決算の期間、ここで分割
        date(2023, 11, 15) # 9/30決算の期間
    ],
    "Code": ["A", "A", "A"],
    "AdjustmentFactor": [1.0, 0.5, 1.0],
})

# --- 2. 修正版メインの処理コード ---

# ステップ1: joinの際に決算日を"ReportDate"として保持
daily_df = prices_df.join_asof(
    statements_df.rename({"Date": "ReportDate", "NumberOfShares": "ReportedShares"}),
    on="Date",
    by="Code"
)

# ステップ2-5: 修正版ロジックを適用
adjusted_df = daily_df.with_columns(
    # ステップ2: "ReportDate"の変わり目を基準にグループIDを作成する【バグ修正点】
    pl.col("ReportDate").rle_id().alias("period_id")
).with_columns(
    # ステップ3 & 4: グループ内で日々の変動率(1/Factor)の累積積を計算
    (1.0 / pl.col("AdjustmentFactor")).cum_prod().over(["Code", "period_id"]).alias("CumulativeRatio")
).with_columns(
    # ステップ5: 決算時点の株式数に、累積の変動率を掛けて、その日の株式数を算出
    (pl.col("ReportedShares") * pl.col("CumulativeRatio")).round(0).cast(pl.Int64).alias("AdjustedNumberOfShares")
)

print(adjusted_df.select(["Date", "Code", "ReportDate", "ReportedShares", "AdjustedNumberOfShares"]))
```
