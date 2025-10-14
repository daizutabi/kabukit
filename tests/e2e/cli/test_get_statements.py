from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = pytest.mark.e2e

runner = CliRunner()


def test_get_statements_all(mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "statements", "--limit", "3"])
    assert result.exit_code == 0
    assert "全銘柄の財務情報を" in result.stdout
    assert "shape:" in result.stdout

    # Verify a file was written to the mocked cache directory
    statements_cache_dir = mock_cache_dir / "statements"
    assert statements_cache_dir.is_dir()
    assert any(statements_cache_dir.iterdir())


def test_get_statements_specific_code(mock_cache_dir: Path) -> None:
    # Use a known, stable code like Toyota (7203)
    result = runner.invoke(app, ["get", "statements", "7203"])
    assert result.exit_code == 0
    assert "shape:" in result.stdout

    statements_cache_dir = mock_cache_dir / "statements"
    assert not statements_cache_dir.exists()
