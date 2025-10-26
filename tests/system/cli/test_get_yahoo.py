from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = pytest.mark.system

runner = CliRunner()


@pytest.fixture
def mock_sub_dir(mock_cache_dir: Path) -> Path:
    return mock_cache_dir / "yahoo" / "quote"


def test_get_yahoo(mock_sub_dir: Path) -> None:
    result = runner.invoke(app, ["get", "yahoo"])

    assert result.exit_code == 1
    assert "--all" in result.stdout
    assert not mock_sub_dir.exists()


@pytest.mark.parametrize("code", ["7203", "72030"])
def test_get_yahoo_code(mock_sub_dir: Path, code: str) -> None:
    result = runner.invoke(app, ["get", "yahoo", code])

    assert result.exit_code == 0
    assert "shape:" in result.stdout
    assert "72030" in result.stdout
    assert not mock_sub_dir.exists()


def test_get_yahoo_all(mock_sub_dir: Path) -> None:
    result = runner.invoke(app, ["get", "yahoo", "--all", "--max-items", "3"])

    assert result.exit_code == 0
    assert "shape:" in result.stdout
    assert not mock_sub_dir.exists()
