from __future__ import annotations

import polars as pl
import pytest

from kabukit.sources.jquants.transform.info import filter_common_stocks, transform

pytestmark = pytest.mark.unit


def test_transform() -> None:
    df = pl.DataFrame(
        {
            "Date": ["2023-01-01", "2023-01-02"],
            "CompanyName": ["A", "B"],
            "Sector17CodeName": ["A", "B"],
            "Sector33CodeName": ["C", "D"],
            "ScaleCategory": ["E", "F"],
            "MarketCodeName": ["G", "H"],
            "MarginCodeName": ["I", "J"],
            "CompanyNameEnglish": ["K", "L"],
        },
    )

    df = transform(df)
    assert df.shape == (2, 7)
    assert df["Date"].dtype == pl.Date
    assert df["Company"].dtype == pl.String
    assert df["Sector17"].dtype == pl.Categorical
    assert df["Sector33"].dtype == pl.Categorical
    assert df["ScaleCategory"].dtype == pl.Categorical
    assert df["Market"].dtype == pl.Categorical
    assert df["Margin"].dtype == pl.Categorical


def test_filter_common_stocks() -> None:
    df = pl.DataFrame(
        {
            "Code": ["0001", "0002", "0003", "0004", "0005"],
            "MarketCodeName": [
                "プライム",
                "TOKYO PRO MARKET",  # フィルタリング対象
                "スタンダード",
                "グロース",
                "プライム",
            ],
            "Sector17CodeName": [
                "情報・通信業",
                "サービス業",
                "その他",  # フィルタリング対象
                "小売業",
                "銀行業",
            ],
            "CompanyName": [
                "A社",
                "B社",
                "C社",
                "D（優先株式）",  # フィルタリング対象
                "E社",
            ],
        },
    )

    result = filter_common_stocks(df)
    assert result["Code"].to_list() == ["0001", "0005"]
