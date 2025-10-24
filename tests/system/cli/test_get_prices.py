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
    return mock_cache_dir / "jquants" / "prices"


def test_get_prices(mock_sub_dir: Path) -> None:
    result = runner.invoke(app, ["get", "prices"])

    assert result.exit_code == 0
    assert "shape:" in result.stdout
    assert not mock_sub_dir.exists()


def test_get_prices_with_code(mock_sub_dir: Path) -> None:
    result = runner.invoke(app, ["get", "prices", "7203"])

    assert result.exit_code == 0
    assert "shape:" in result.stdout
    assert "72030" in result.stdout
    assert not mock_sub_dir.exists()


def test_get_prices_with_date(mock_sub_dir: Path) -> None:
    result = runner.invoke(app, ["get", "prices", "20230104"])

    assert result.exit_code == 0
    assert "shape:" in result.stdout
    assert "2023-01-04" in result.stdout
    assert not mock_sub_dir.exists()


def test_get_prices_all(mock_sub_dir: Path) -> None:
    result = runner.invoke(app, ["get", "prices", "--all", "--max-items", "3"])

    assert result.exit_code == 0
    assert "shape:" in result.stdout
    assert not mock_sub_dir.exists()
