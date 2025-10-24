from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = pytest.mark.system

runner = CliRunner()


def remove_ansi(text: str) -> str:
    return re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", text)


def test_cache_tree_system(mock_cache_dir: Path) -> None:
    """System test for 'kabu cache tree' command.

    Verifies that it correctly lists contents of a real (mocked) cache directory.
    """
    # Populate cache with some dummy data using a 'get' command
    result_get = runner.invoke(app, ["get", "info"])
    assert result_get.exit_code == 0

    # Now run cache tree and assert its output
    result_tree = runner.invoke(app, ["cache", "tree"])
    assert result_tree.exit_code == 0

    output = remove_ansi(result_tree.stdout.replace("\n", ""))
    assert str(mock_cache_dir) in output
    assert "info" in result_tree.stdout
    sub_dir = mock_cache_dir / "jquants" / "info"
    files = sub_dir.iterdir()
    assert any(f.name in result_tree.stdout for f in files)


def test_cache_clean_system(mock_cache_dir: Path) -> None:
    """System test for 'kabu cache clean' command.

    Verifies that it correctly removes a real (mocked) cache directory.
    """
    # Populate cache with some dummy data using a 'get' command
    result_get = runner.invoke(app, ["get", "info"])
    assert result_get.exit_code == 0
    assert mock_cache_dir.is_dir()
    assert any(mock_cache_dir.iterdir())

    # Now run cache clean and assert its output
    result_clean = runner.invoke(app, ["cache", "clean"])
    assert result_clean.exit_code == 0
    msg = f"キャッシュディレクトリ '{mock_cache_dir}' を正常にクリーンアップしました。"
    assert msg in result_clean.stdout
    assert not mock_cache_dir.exists()
