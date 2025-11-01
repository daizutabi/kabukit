from __future__ import annotations

from typing import Any

import polars as pl
import pytest

from kabukit.cli.utils import display_dataframe, display_value

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def df() -> pl.DataFrame:
    return pl.DataFrame({"col1": [1, 2], "col2": ["abc", "def"]})


def test_display_dataframe_empty(capsys: pytest.CaptureFixture[str]) -> None:
    display_dataframe(pl.DataFrame())

    assert "取得したデータはありません。" in capsys.readouterr().out


def test_display_dataframe(
    df: pl.DataFrame,
    capsys: pytest.CaptureFixture[str],
) -> None:
    display_dataframe(df)

    assert "shape: (2, 2)" in capsys.readouterr().out


def test_display_dataframe_quiet(
    df: pl.DataFrame,
    capsys: pytest.CaptureFixture[str],
) -> None:
    display_dataframe(df, quiet=True)

    assert capsys.readouterr().out == ""


def test_display_single_row_dataframe(
    df: pl.DataFrame,
    capsys: pytest.CaptureFixture[str],
) -> None:
    display_dataframe(df.head(1))

    assert "width: 2" in capsys.readouterr().out


def test_display_dataframe_first(
    df: pl.DataFrame,
    capsys: pytest.CaptureFixture[str],
) -> None:
    display_dataframe(df, first=True)

    out = capsys.readouterr().out
    assert "width: 2" in out
    assert "abc" in out


def test_display_dataframe_last(
    df: pl.DataFrame,
    capsys: pytest.CaptureFixture[str],
) -> None:
    display_dataframe(df, last=True)

    out = capsys.readouterr().out
    assert "width: 2" in out
    assert "def" in out


@pytest.mark.parametrize(
    ("value", "expected"),
    [("a", "a"), (123, "123"), (12.34, "12.34"), (1e10, "10,000,000,000.0")],
)
def test_display_value(value: Any, expected: str) -> None:
    assert display_value(value) == expected
