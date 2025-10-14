from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = pytest.mark.system

runner = CliRunner()


def test_get_info_all(mock_cache_dir: Path) -> None:
    """Test 'kabu get info' to retrieve all listed info and save to cache."""
    result = runner.invoke(app, ["get", "info"])
    assert result.exit_code == 0
    assert "全銘柄の情報を" in result.stdout
    assert "Code" in result.stdout
    assert "CompanyName" in result.stdout

    # Verify a file was written to the mocked cache directory
    info_cache_dir = mock_cache_dir / "info"
    assert info_cache_dir.is_dir()
    assert any(info_cache_dir.iterdir())  # Check if any file exists in the directory


def test_get_info_specific_code(mock_cache_dir: Path) -> None:
    """Test 'kabu get info <code_id>' to retrieve info for a specific code."""
    # Use a known, stable code like Toyota (7203)
    result = runner.invoke(app, ["get", "info", "7203"])
    assert result.exit_code == 0
    assert "7203" in result.stdout
    assert "トヨタ自動車" in result.stdout
    assert "Code" in result.stdout
    assert "CompanyName" in result.stdout

    info_cache_dir = mock_cache_dir / "info"
    assert not info_cache_dir.exists()
