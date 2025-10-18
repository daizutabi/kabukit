from __future__ import annotations

import re
import sys

import pytest

pytestmark = pytest.mark.unit


@pytest.mark.skipif(sys.platform != "linux", reason="This test is for Linux")
def test_get_cache_dir_linux() -> None:
    from kabukit.utils.config import get_cache_dir

    result = get_cache_dir()
    pattern = r"^/home/\S+/\.cache/kabukit$"
    assert re.match(pattern, str(result))


@pytest.mark.skipif(sys.platform != "darwin", reason="This test is for macOS")
def test_get_cache_dir_darwin() -> None:
    from kabukit.utils.config import get_cache_dir

    result = get_cache_dir()
    pattern = r"^/Users/\S+/Library/Caches/kabukit$"
    assert re.match(pattern, str(result))


@pytest.mark.skipif(sys.platform != "win32", reason="This test is for Windows")
def test_get_cache_dir_windows() -> None:
    from kabukit.utils.config import get_cache_dir

    result = get_cache_dir()
    pattern = r"^C:\\Users\\\S+\\AppData\\Local\\kabukit\\Cache$"
    assert re.match(pattern, str(result))
