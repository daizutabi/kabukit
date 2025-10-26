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
    return mock_cache_dir / "tdnet" / "list"


def test_get_tdnet(mock_sub_dir: Path) -> None:
    result = runner.invoke(app, ["get", "tdnet"])

    assert result.exit_code == 0
    assert "shape:" in result.stdout
    assert not mock_sub_dir.exists()


def test_get_tdnet_date(mock_sub_dir: Path) -> None:
    from kabukit.utils.datetime import today

    date = today(as_str=True)
    result = runner.invoke(app, ["get", "tdnet", date])

    assert result.exit_code == 0
    assert "shape:" in result.stdout
    assert not mock_sub_dir.exists()


def test_get_tdnet_all(mock_sub_dir: Path) -> None:
    result = runner.invoke(app, ["get", "tdnet", "--all", "--max-items", "3"])

    assert result.exit_code == 0
    assert "shape:" in result.stdout
    assert not mock_sub_dir.exists()
