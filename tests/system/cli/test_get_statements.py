from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = pytest.mark.system

runner = CliRunner()


def test_get_statements_with_code(mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "statements", "7203"])
    assert result.exit_code == 0
    assert "shape:" in result.stdout

    statements_cache_dir = mock_cache_dir / "jquants" / "statements"
    assert not statements_cache_dir.exists()


def test_get_statements_without_code(mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "statements", "--max-items", "3"])
    assert result.exit_code == 0
    assert "全銘柄の財務情報を" in result.stdout
    assert "shape:" in result.stdout

    statements_cache_dir = mock_cache_dir / "jquants" / "statements"
    assert statements_cache_dir.is_dir()
    assert any(statements_cache_dir.iterdir())
