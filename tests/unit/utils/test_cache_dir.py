from __future__ import annotations

import re
import sys

import pytest

pytestmark = pytest.mark.unit


@pytest.mark.skipif(sys.platform != "linux", reason="This test is for Linux")
def test_get_cache_dir_linux() -> None:
    from kabukit.utils.config import get_cache_dir

    result = get_cache_dir()
    pattern = re.compile(r"^/home/\S+/\.cache/kabukit$")
    assert pattern.match(str(result))


@pytest.mark.skipif(sys.platform != "darwin", reason="This test is for macOS")
def test_get_cache_dir_darwin() -> None:
    from kabukit.utils.config import get_cache_dir

    result = get_cache_dir()
    pattern = re.compile(r"^/Users/\S+/Library/Caches/kabukit$")
    assert pattern.match(str(result))


@pytest.mark.skipif(sys.platform != "win32", reason="This test is for Windows")
def test_get_cache_dir_windows() -> None:
    from kabukit.utils.config import get_cache_dir

    result = get_cache_dir()
    pattern = re.compile(r"^C:\Users\S+\AppData\Local\kabukit\Cache$")
    assert pattern.match(str(result))
