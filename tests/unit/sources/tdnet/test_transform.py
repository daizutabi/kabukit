from __future__ import annotations

import datetime

import polars as pl
import pytest

from kabukit.sources.tdnet.columns import ListColumns
from kabukit.sources.tdnet.transform import transform_list

pytestmark = pytest.mark.unit


def test_transform_list() -> None:
    df = pl.DataFrame(
        {
            "Code": ["1234", "5678"],
            "DisclosedTime": [None, None],
            "Title": ["Title1", "Title2"],
        },
    )
    date = datetime.date(2024, 6, 20)
    df = transform_list(df, date)
    assert df.columns == ["Code", "DisclosedDate", "DisclosedTime", "Title"]
    assert df["DisclosedDate"].unique().to_list() == [date]

    df = ListColumns.rename(df, strict=False)
    assert df.columns == ["銘柄コード", "開示日", "開示時刻", "表題"]
