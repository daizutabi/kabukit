import subprocess

import pytest

pytestmark = pytest.mark.e2e


def test_command():
    """
    Tests that the installed `kabu` command runs correctly.

    This is an end-to-end test that requires the package to be installed
    in editable mode.
    """
    out = subprocess.check_output(["kabu", "version"], text=True)
    assert "kabukit" in out
    assert out.count(".") == 2
