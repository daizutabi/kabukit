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
    return mock_cache_dir / "jpx" / "shares"


def test_get_shares(mock_sub_dir: Path) -> None:
    result = runner.invoke(app, ["get", "shares", "--max-items", "1"])

    assert result.exit_code == 0
    assert "shape:" in result.stdout
    assert not mock_sub_dir.exists()
