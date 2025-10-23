from __future__ import annotations

import subprocess

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

pytestmark = pytest.mark.system

runner = CliRunner()


def test_app_invoke():
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "kabukit version" in result.stdout
    assert result.stdout.count(".") == 2


def test_app_subprocess():
    output = subprocess.check_output(["kabu", "version"], text=True)

    assert "kabukit version" in output
    assert output.count(".") == 2
