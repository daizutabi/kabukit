from __future__ import annotations

import polars as pl
import pytest

from kabukit.cli.utils import display_dataframe

pytestmark = pytest.mark.unit


def test_display_dataframe_empty(capsys: pytest.CaptureFixture[str]) -> None:
    display_dataframe(pl.DataFrame())

    assert "取得したデータはありません。" in capsys.readouterr().out


def test_display_dataframe(capsys: pytest.CaptureFixture[str]) -> None:
    display_dataframe(pl.DataFrame({"col1": [1, 2], "col2": ["a", "b"]}))

    assert "shape: (2, 2)" in capsys.readouterr().out
