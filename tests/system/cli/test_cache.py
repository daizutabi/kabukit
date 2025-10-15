from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = pytest.mark.system

runner = CliRunner()


def test_cache_tree_system(mock_cache_dir: Path) -> None:
    """
    System test for 'kabu cache tree' command.
    Verifies that it correctly lists contents of a real (mocked) cache directory.
    """
    # Populate cache with some dummy data using a 'get' command
    args = ["get", "statements", "--max-items", "2"]
    result_get = runner.invoke(app, args)
    assert result_get.exit_code == 0

    # Now run cache tree and assert its output
    result_tree = runner.invoke(app, ["cache", "tree"])
    assert result_tree.exit_code == 0
    assert str(mock_cache_dir) in result_tree.stdout
    assert "statements" in result_tree.stdout
    files = (mock_cache_dir / "statements").iterdir()
    assert any(f.name in result_tree.stdout for f in files)


def test_cache_clean_system(mock_cache_dir: Path) -> None:
    """
    System test for 'kabu cache clean' command.
    Verifies that it correctly removes a real (mocked) cache directory.
    """
    # Populate cache with some dummy data using a 'get' command
    args = ["get", "prices", "--max-items", "2"]
    result_get = runner.invoke(app, args)
    assert result_get.exit_code == 0
    assert mock_cache_dir.is_dir()
    assert any(mock_cache_dir.iterdir())

    # Now run cache clean and assert its output
    result_clean = runner.invoke(app, ["cache", "clean"])
    assert result_clean.exit_code == 0
    msg = f"キャッシュディレクトリ '{mock_cache_dir}' を正常にクリーンアップしました。"
    assert msg in result_clean.stdout
    assert not mock_cache_dir.exists()
