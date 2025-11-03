from __future__ import annotations

import polars as pl
import pytest

from kabukit.sources.tdnet.columns import ListColumns
from kabukit.sources.tdnet.transform import transform_list

pytestmark = pytest.mark.unit


def test_transform_list() -> None:
    df = pl.DataFrame({"Code": ["1234", "5678"], "Title": [None, None]})
    df = transform_list(df)
    assert df.columns == ["Code", "Title"]
    assert df["Title"].dtype == pl.String

    df = ListColumns.rename(df, strict=False)
    assert df.columns == ["銘柄コード", "表題"]
