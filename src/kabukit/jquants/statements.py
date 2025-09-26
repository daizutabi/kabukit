from __future__ import annotations

import datetime
from functools import cache
from typing import TYPE_CHECKING

import holidays
import polars as pl

if TYPE_CHECKING:
    from polars import DataFrame


def clean(df: DataFrame) -> DataFrame:
    return (
        df.select(pl.exclude(r"^.*\(REIT\)|.*NonConsolidated.*$"))
        .rename(
            {
                "DisclosedDate": "Date",
                "DisclosedTime": "Time",
                "LocalCode": "Code",
                "NumberOfIssuedAndOutstandingSharesAtTheEndOfFiscalYearIncludingTreasuryStock": "NumberOfShares",  # noqa: E501
                "NumberOfTreasuryStockAtTheEndOfFiscalYear": "NumberOfTreasuryStock",
            },
        )
        .with_columns(
            pl.col("^.*Date$").str.to_date("%Y-%m-%d", strict=False),
            pl.col("Time").str.to_time("%H:%M:%S", strict=False),
            pl.col("TypeOfCurrentPeriod").cast(pl.Categorical),
        )
        .pipe(_cast_float)
        .pipe(_cast_bool)
    )


def _cast_float(df: DataFrame) -> DataFrame:
    return df.with_columns(
        pl.col(f"^.*{name}.*$").cast(pl.Float64, strict=False)
        for name in [
            "Assets",
            "BookValue",
            "Cash",
            "Distributions",
            "Dividend",
            "Earnings",
            "Equity",
            "NetSales",
            "NumberOf",
            "PayoutRatio",
            "Profit",
        ]
    )


def _cast_bool(df: DataFrame) -> DataFrame:
    columns = df.select(pl.col("^.*Changes.*$")).columns
    columns.append("RetrospectiveRestatement")

    return df.with_columns(
        pl.when(pl.col(col) == "true")
        .then(True)  # noqa: FBT003
        .when(pl.col(col) == "false")
        .then(False)  # noqa: FBT003
        .otherwise(None)
        .alias(col)
        for col in columns
    )


@cache
def get_holidays(year: int | None = None, n: int = 10) -> list[datetime.date]:
    """指定した過去年数の日本の祝日を取得する。"""
    if year is None:
        year = datetime.datetime.now().year  # noqa: DTZ005

    dates = holidays.country_holidays("JP", years=range(year - n, year + 1))
    return sorted(dates.keys())


def update_effective_date(df: DataFrame, year: int | None = None) -> DataFrame:
    """開示日が休日や15時以降の場合、翌営業日に更新する。"""
    holidays = get_holidays(year=year)

    cond = pl.col("Time").is_null() | (pl.col("Time") > datetime.time(15, 0))

    return df.with_columns(
        pl.when(cond)
        .then(pl.col("Date").dt.add_business_days(1, holidays=holidays))
        .otherwise(pl.col("Date"))
        .alias("Date"),
    )
