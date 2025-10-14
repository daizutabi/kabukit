from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.e2e

runner = CliRunner()


@pytest.fixture
def mock_cache_dir(tmp_path: Path, mocker: MockerFixture) -> Path:
    """Create a temporary cache directory and mock get_cache_dir for E2E tests."""
    # For E2E tests, we want to mock the cache directory to a temporary path
    # to avoid polluting the actual cache and ensure test isolation.
    mocker.patch("kabukit.core.base.get_cache_dir", return_value=tmp_path)
    mocker.patch("kabukit.cli.cache.get_cache_dir", return_value=tmp_path)
    return tmp_path


def test_get_entries_all(mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "entries", "--limit", "3"])
    assert result.exit_code == 0
    assert "書類一覧を" in result.stdout
    assert "shape:" in result.stdout

    # Verify a file was written to the mocked cache directory
    entries_cache_dir = mock_cache_dir / "entries"
    assert entries_cache_dir.is_dir()
    assert any(entries_cache_dir.iterdir())  # Check if any file exists in the directory


def test_get_entries_specific_date(mock_cache_dir: Path) -> None:
    """Test 'kabu get entries <date>' to retrieve entries for a specific date."""
    # Use a known date with expected entries
    result = runner.invoke(app, ["get", "entries", "2023-01-01"])
    assert result.exit_code == 0
    assert "shape:" in result.stdout

    entries_cache_dir = mock_cache_dir / "entries"
    assert not entries_cache_dir.exists()
