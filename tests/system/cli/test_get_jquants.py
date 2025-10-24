from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = pytest.mark.system

runner = CliRunner()


def test_get_jquants_all(mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "jquants", "--all", "--max-items", "3"])

    assert result.exit_code == 0
    assert "上場銘柄一覧を取得します。" in result.stdout
    assert "財務情報を取得します。" in result.stdout
    assert "株価情報を取得します。" in result.stdout

    assert (mock_cache_dir / "jquants" / "info").exists()
    assert any((mock_cache_dir / "jquants" / "info").glob("*.parquet"))
    assert not (mock_cache_dir / "jquants" / "statements").exists()
    assert not (mock_cache_dir / "jquants" / "prices").exists()
