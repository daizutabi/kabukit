from __future__ import annotations

import polars as pl
import pytest
from polars.testing import assert_frame_equal

pytestmark = pytest.mark.unit


def test_parse() -> None:
    from kabukit.sources.yahoo.parsers.quote import parse

    text = """\
        <script>
            window.__PRELOADED_STATE__ = {"key": "value"};
        </script>
    """
    df = parse(text)
    # assert df["Code"].unique().to_list() == ["12340"]
    assert not df.is_empty()


def test_parse_empty() -> None:
    from kabukit.sources.yahoo.parsers.quote import parse

    df = parse("")
    assert_frame_equal(df, pl.DataFrame())
