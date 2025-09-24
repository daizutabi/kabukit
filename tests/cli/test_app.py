import subprocess

from typer.testing import CliRunner

from kabukit.cli.app import app

runner = CliRunner()


def test_invoke():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "kabukit" in result.stdout
    assert result.stdout.count(".") == 2


def test_command():
    out = subprocess.check_output(["kabu", "version"], text=True)
    assert "kabukit" in out
    assert out.count(".") == 2
