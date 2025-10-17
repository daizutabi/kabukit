from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.integration

runner = CliRunner()


@pytest.fixture
def mock_cache_dir(tmp_path: Path, mocker: MockerFixture) -> Path:
    """Create a temporary cache directory and mock get_cache_dir for tests."""
    # For integration tests, we want to mock the cache directory to a temporary path
    # to avoid polluting the actual cache and ensure test isolation.
    mocker.patch("kabukit.cli.cache.get_cache_dir", return_value=tmp_path)
    return tmp_path


def test_cache_tree(mock_cache_dir: Path):
    (mock_cache_dir / "info").mkdir()
    (mock_cache_dir / "info/dummy_file.txt").touch()

    result = runner.invoke(app, ["cache", "tree"])
    assert result.exit_code == 0
    assert str(mock_cache_dir) in result.stdout
    assert "info" in result.stdout
    assert "dummy_file.txt (0 B)" in result.stdout


def test_cache_tree_error(mock_cache_dir: Path):
    mock_cache_dir.rmdir()

    result = runner.invoke(app, ["cache", "tree"])
    assert result.exit_code == 0
    assert "存在しません" in result.stdout


def test_cache_clean(mock_cache_dir: Path):
    dummy_dir = mock_cache_dir / "dummy_dir"
    dummy_dir.mkdir()
    (dummy_dir / "dummy_file.txt").touch()

    result = runner.invoke(app, ["cache", "clean"])
    assert result.exit_code == 0

    msg = f"キャッシュディレクトリ '{mock_cache_dir}' を正常にクリーンアップしました。"
    assert msg in result.stdout
    assert not mock_cache_dir.exists()
