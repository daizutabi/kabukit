from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = pytest.mark.system

runner = CliRunner()


def test_get_jquants(mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "jquants", "--max-items", "3"])

    assert result.exit_code == 0
    assert "上場銘柄一覧を取得します。" in result.stdout
    assert "財務情報を取得します。" in result.stdout
    assert "株価情報を取得します。" in result.stdout

    # Verify cache directories and files
    expected_cache_dirs = {
        "jquants": ["info", "statements", "prices"],
    }
    for source, groups in expected_cache_dirs.items():
        for group in groups:
            cache_path = mock_cache_dir / source / group
            assert cache_path.is_dir()
            assert any(cache_path.iterdir())
