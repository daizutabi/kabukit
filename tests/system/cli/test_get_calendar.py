from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = pytest.mark.system

runner = CliRunner()


def test_get_calendar(mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "calendar"])

    assert result.exit_code == 0
    assert "Date" in result.stdout
    assert "HolidayDivision" in result.stdout
    assert "IsHoliday" in result.stdout

    calendar_cache_dir = mock_cache_dir / "jquants" / "calendar"
    assert calendar_cache_dir.exists()
