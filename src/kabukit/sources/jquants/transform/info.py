from __future__ import annotations

import polars as pl

from kabukit.models.jquants.info import InfoDataFrame
from kabukit.sources.utils import normalize_code


def transform(df: pl.DataFrame) -> InfoDataFrame:
    df = filter_common_stocks(df)

    if df.is_empty():
        return InfoDataFrame()

    return (
        df
        .pipe(normalize_code)
        .with_columns(
            pl.col("Date").str.to_date("%Y-%m-%d"),
        )
        .drop("^.+Code$", "CompanyNameEnglish")
        .rename(
            {
                "CompanyName": "Company",
                "Sector17CodeName": "Sector17",
                "Sector33CodeName": "Sector33",
                "MarketCodeName": "Market",
                "MarginCodeName": "Margin",
            },
        )
        .pipe(InfoDataFrame)
        .validate()
    )


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
