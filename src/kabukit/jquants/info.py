from __future__ import annotations

import polars as pl
from polars import DataFrame


def clean(df: DataFrame) -> DataFrame:
    return df.with_columns(
        pl.col("Date").str.to_date("%Y-%m-%d"),
        pl.col("^.*CodeName$", "ScaleCategory").cast(pl.Categorical),
    ).drop("^.+Code$", "CompanyNameEnglish")


async def get_codes() -> list[str]:
    """銘柄コードのリストを返す。

    市場「TOKYO PRO MARKET」と業種「その他」を除外した銘柄を対象とする。
    """
    from .client import JQuantsClient

    async with JQuantsClient() as client:
        info = await client.get_info()

    return (
        info.filter(
            pl.col("MarketCodeName") != "TOKYO PRO MARKET",
            pl.col("Sector17CodeName") != "その他",
        )
        .get_column("Code")
        .to_list()
    )
