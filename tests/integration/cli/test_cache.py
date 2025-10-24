from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = pytest.mark.integration

runner = CliRunner()


def remove_ansi(text: str) -> str:
    return re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", text)


def test_cache_tree(mock_cache_dir: Path):
    (mock_cache_dir / "info").mkdir()
    (mock_cache_dir / "info/dummy_file.txt").touch()

    result = runner.invoke(app, ["cache", "tree"])
    assert result.exit_code == 0

    output = remove_ansi(result.stdout.replace("\n", ""))
    assert str(mock_cache_dir) in output
    assert "info" in result.stdout
    assert "dummy_file.txt" in result.stdout
    assert "0 B" in result.stdout


def test_cache_tree_error(mock_cache_dir: Path):
    mock_cache_dir.rmdir()

    result = runner.invoke(app, ["cache", "tree"])
    assert result.exit_code == 0
    assert "存在しません" in result.stdout


def test_cache_clean(mock_cache_dir: Path):
    dummy_dir = mock_cache_dir / "dummy_dir"
    dummy_dir.mkdir()
    (dummy_dir / "dummy_file.txt").touch()

    result = runner.invoke(app, ["cache", "clean", "dummy_dir"])
    assert result.exit_code == 0

    msg = f"キャッシュディレクトリ '{dummy_dir}' を正常にクリーンアップしました。"
    assert msg in result.stdout
    assert not dummy_dir.exists()
    assert mock_cache_dir.exists()


def test_cache_clean_all(mock_cache_dir: Path):
    dummy_dir = mock_cache_dir / "dummy_dir"
    dummy_dir.mkdir()
    (dummy_dir / "dummy_file.txt").touch()

    result = runner.invoke(app, ["cache", "clean", "--all"])
    assert result.exit_code == 0

    msg = f"キャッシュディレクトリ '{mock_cache_dir}' を正常にクリーンアップしました。"
    assert msg in result.stdout
    assert not mock_cache_dir.exists()
