from __future__ import annotations

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

pytestmark = pytest.mark.integration

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "kabukit version" in result.stdout
