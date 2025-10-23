from __future__ import annotations

import polars as pl


def clean(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.col("Date").str.to_date("%Y-%m-%d"),
        pl.col("^.*CodeName$", "ScaleCategory").cast(pl.Categorical),
    ).drop("^.+Code$", "CompanyNameEnglish")


def filter_common_stocks(df: pl.DataFrame) -> pl.DataFrame:
    """分析対象となる銘柄でフィルタリングする。

    以下の条件を満たす銘柄は対象外とする。

    - 市場: TOKYO PRO MARKET
    - 業種: その他 -- (投資信託など)
    - 優先株式

    Returns:
        pl.DataFrame: 分析対象となる銘柄でフィルタリングされたDataFrame。
    """
    return df.filter(
        pl.col("MarketCodeName") != "TOKYO PRO MARKET",
        pl.col("Sector17CodeName") != "その他",
        ~pl.col("CompanyName").str.contains("優先株式"),
    )
