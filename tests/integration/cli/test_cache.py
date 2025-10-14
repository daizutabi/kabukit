from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

runner = CliRunner()


def test_cache_tree(mock_cache_dir: Path):
    (mock_cache_dir / "dummy_file.txt").touch()

    result = runner.invoke(app, ["cache", "tree"])
    assert result.exit_code == 0
    assert str(mock_cache_dir) in result.stdout
    assert "dummy_file.txt" in result.stdout


def test_cache_clean(mock_cache_dir: Path):
    dummy_dir = mock_cache_dir / "dummy_dir"
    dummy_dir.mkdir()
    (dummy_dir / "dummy_file.txt").touch()

    result = runner.invoke(app, ["cache", "clean"])
    assert result.exit_code == 0

    msg = f"キャッシュディレクトリ '{mock_cache_dir}' を正常にクリーンアップしました。"
    assert msg in result.stdout
    assert not mock_cache_dir.exists()
