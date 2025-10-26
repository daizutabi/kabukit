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


def test_parse() -> None:
    from kabukit.sources.yahoo.parser import parse

    text = """\
        <script>
            window.__PRELOADED_STATE__ = {"key": "value"};
        </script>
    """
    df = parse(text, "12340")
    assert df["Code"].unique().to_list() == ["12340"]


def test_parse_empty() -> None:
    from kabukit.sources.yahoo.parser import parse

    df = parse("", "12340")
    assert_frame_equal(df, pl.DataFrame())
