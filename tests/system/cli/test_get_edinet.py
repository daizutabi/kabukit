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
    return mock_cache_dir / "edinet" / "list"


def test_get_edinet(mock_sub_dir: Path) -> None:
    result = runner.invoke(app, ["get", "edinet"])

    assert result.exit_code == 0
    assert "shape:" in result.stdout
    assert not mock_sub_dir.exists()


def test_get_tdnet_date(mock_sub_dir: Path) -> None:
    result = runner.invoke(app, ["get", "edinet", "20251023"])

    assert result.exit_code == 0
    assert "shape:" in result.stdout
    assert "2025-10-23" in result.stdout
    assert not mock_sub_dir.exists()


def test_get_tdnet_all(mock_sub_dir: Path) -> None:
    result = runner.invoke(app, ["get", "edinet", "--all", "--max-items", "3"])

    assert result.exit_code == 0
    assert "shape:" in result.stdout
    assert not mock_sub_dir.exists()
