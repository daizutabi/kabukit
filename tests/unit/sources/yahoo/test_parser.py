from __future__ import annotations

import polars as pl
import pytest
from polars.testing import assert_frame_equal

pytestmark = pytest.mark.unit


def test_get_preloaded_state() -> None:
    from kabukit.sources.yahoo.parser import get_preloaded_state

    text = """\
        <script>
            window.__PRELOADED_STATE__ = {"key": "value"};
        </script>
    """
    result = get_preloaded_state(text)
    assert result == {"key": "value"}


def test_get_preloaded_state_no_tag() -> None:
    from kabukit.sources.yahoo.parser import get_preloaded_state

    text = """\
        <a>
            window.__PRELOADED_STATE__ = {"key": "value"};
        </a>
    """
    assert get_preloaded_state(text) == {}


def test_parse_quote() -> None:
    from kabukit.sources.yahoo.parser import parse_quote

    text = """\
        <script>
            window.__PRELOADED_STATE__ = {"key": "value"};
        </script>
    """
    df = parse_quote(text)
    # assert df["Code"].unique().to_list() == ["12340"]
    assert not df.is_empty()


def test_parse_quote_empty() -> None:
    from kabukit.sources.yahoo.parser import parse_quote

    df = parse_quote("")
    assert_frame_equal(df, pl.DataFrame())
