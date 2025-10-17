import pytest
from polars import DataFrame

from kabukit.sources.jquants.schema import (
    InfoColumns,
    PriceColumns,
    StatementColumns,
    rename,
)

pytestmark = pytest.mark.unit


def test_rename_all_columns() -> None:
    """DataFrameの列名が日本語から英語に正しく変換されることを確認する。"""
    rename_map = {
        **{c.name: c.value for c in InfoColumns},
        **{c.name: c.value for c in PriceColumns},
        **{c.name: c.value for c in StatementColumns},
    }

    test_data = {
        # InfoColumns
        "Code": ["7203"],
        "CompanyName": ["トヨタ自動車"],
        # PriceColumns
        "Open": [3000.0],
        "Close": [3100.0],
        # StatementColumns
        "NetSales": [1000000],
        "Profit": [50000],
        "TotalAssets": [2000000],
        "Equity": [1200000],
    }
    df = DataFrame(test_data)

    # 変換を実行
    renamed_df = rename(df)

    # 期待されるカラム名
    expected_columns = [rename_map[col] for col in test_data]

    # カラム名が正しく変換されたか検証
    assert renamed_df.columns == expected_columns
