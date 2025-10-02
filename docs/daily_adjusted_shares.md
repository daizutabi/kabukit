# 日次調整済み株式数の計算ロジック

## 概要

四半期ごとにしか発表されない株式数を、日々の株価データに追従させ、株式分割・併合の影響を正しく反映させるための`polars`を使った実装方法を記録する。

このドキュメントは、`kabukit.core.prices.Prices.with_adjusted_shares`メソッドの背景となる計算ロジックを解説する。

## 前提データ

以下の2つのデータソースが存在することを前提とする。

1.  **財務データ (`statements`)**
    *   **主なカラム**: `DisclosedDate`, `DisclosedTime`, `Code`, `TotalShares`, `TreasuryShares`
    *   **特徴**: データは四半期ごとなど、特定の日にのみ存在する。

2.  **株価データ (`prices`)**
    *   **主なカラム**: `Date`, `Code`, `AdjustmentFactor`
    *   **特徴**: データは営業日毎日存在する。`AdjustmentFactor`は株式分割や併合の権利落ち日にのみ比率が記録され、それ以外の日は`1.0`となる。

## 計算ロジック

### 1. 有効日の決定 (Effective Date)

決算発表が取引時間後（15時以降）や非営業日に行われた場合、その情報は翌営業日から市場で利用可能になる。そのため、`statements`の`DisclosedDate`と`DisclosedTime`を元に、実際に株価と紐づけるべき「有効日」としての`Date`列を計算する。

### 2. 最新の株式数のマッピング

`prices`の各行に対して、ステップ1で計算した`statements`の有効日`Date`をキーとして`join_asof`を実行する。これにより、各営業日に、その日以前の最新の決算情報（`TotalShares`など）が紐付く。この際、計算期間をグループ化するために、元の開示日も`ReportDate`のような名前で保持しておく。

### 3. 計算期間のグループ化

計算は、決算短信が切り替わるタイミングでリセットする必要がある。そのため、処理を`Code`（銘柄）と`ReportDate`（決算日）でグループ化する。

### 4. 累積変動率の計算

`AdjustmentFactor`は株価に乗算する係数なので、株式数に対してはその逆数を適用する。ステップ3のグループ内で、日々の株式数変動率（`1.0 / AdjustmentFactor`）の**累積積 (`cum_prod`)** を計算し、`CumulativeRatio`（累積変動率）を求める。

### 5. 日次株式数の算出と命名

ステップ2でマッピングした決算時点の株式数（例: `TotalShares`）に、ステップ4で計算した`CumulativeRatio`を掛け合わせることで、その日の正しい株式数が求まる。

計算結果の列は、元の情報と区別するために、`Adjusted`という接頭辞を付けて命名する（例: `AdjustedTotalShares`）。

## 実装コード例 (polars)

```python
import polars as pl
from datetime import date, time, timedelta

# --- 1. 前提データの準備 ---
prices_df = pl.DataFrame(
    {
        "Date": [date(2023, 5, 1), date(2023, 7, 15), date(2023, 8, 1)],
        "Code": ["A", "A", "A"],
        "AdjustmentFactor": [1.0, 0.5, 1.0],
    }
)

statements_df = pl.DataFrame(
    {
        "DisclosedDate": [date(2023, 3, 31), date(2023, 6, 30)],
        "DisclosedTime": [time(16, 0), time(15, 30)],
        "Code": ["A", "A"],
        "TotalShares": [1000, 1200],
        "TreasuryShares": [100, 120],
    }
)


# --- 2. 計算ロジックの実行 ---

# ステップ1: 有効日の決定
# (簡単のため、ここでは単純に+1日する。実際の実装では祝日を考慮した翌営業日を計算)
statements_with_date = statements_df.with_columns(
    (pl.col("DisclosedDate") + timedelta(days=1)).alias("Date"),
    pl.col("DisclosedDate").alias("ReportDate"),
)

# ステップ2: 最新の株式数のマッピング
daily_df = prices_df.join_asof(
    statements_with_date,
    on="Date",
    by="Code",
)

# ステップ3-5: グループ化、計算、命名
adjusted_df = daily_df.with_columns(
    # ステップ4: 累積変動率の計算
    (1.0 / pl.col("AdjustmentFactor"))
    .cum_prod()
    .over(["Code", "ReportDate"])
    .alias("CumulativeRatio")
).with_columns(
    # ステップ5: 日次株式数の算出と命名
    (pl.col("TotalShares") * pl.col("CumulativeRatio"))
    .round(0)
    .cast(pl.Int64)
    .name.prefix("Adjusted")
)

print(
    adjusted_df.select(
        "Date", "Code", "ReportDate", "TotalShares", "AdjustedTotalShares"
    )
)
```
