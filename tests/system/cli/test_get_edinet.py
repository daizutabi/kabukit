from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = pytest.mark.system

runner = CliRunner()


def test_get_edinet_list_with_date(mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "edinet", "2023-01-01"])

    assert result.exit_code == 0
    assert "shape:" in result.stdout

    edinet_list_cache_dir = mock_cache_dir / "edinet" / "list"
    assert not edinet_list_cache_dir.exists()


def test_get_edinet_list_without_date(mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "edinet", "--max-items", "3"])

    assert result.exit_code == 0
    assert "書類一覧を" in result.stdout
    assert "shape:" in result.stdout

    edinet_list_cache_dir = mock_cache_dir / "edinet" / "list"
    assert edinet_list_cache_dir.is_dir()
    assert any(edinet_list_cache_dir.iterdir())
