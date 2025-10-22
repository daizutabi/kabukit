from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = pytest.mark.system

runner = CliRunner()


def mock_get_edinet_list_all(mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "entries", "--max-items", "3"])
    assert result.exit_code == 0
    assert "書類一覧を" in result.stdout
    assert "shape:" in result.stdout

    entries_cache_dir = mock_cache_dir / "edinet" / "entries"
    assert entries_cache_dir.is_dir()
    assert any(entries_cache_dir.iterdir())  # Check if any file exists in the directory


def mock_get_edinet_list_specific_date(mock_cache_dir: Path) -> None:
    """Test 'kabu get entries <date>' to retrieve entries for a specific date."""
    # Use a known date with expected entries
    result = runner.invoke(app, ["get", "entries", "2023-01-01"])
    assert result.exit_code == 0
    assert "shape:" in result.stdout

    entries_cache_dir = mock_cache_dir / "entries"
    assert not entries_cache_dir.exists()
