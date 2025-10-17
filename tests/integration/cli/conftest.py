from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


@pytest.fixture
def mock_cache_dir(tmp_path: Path, mocker: MockerFixture) -> Path:
    """Create a temporary cache directory and mock get_cache_dir."""
    mocker.patch("kabukit.core.base.get_cache_dir", return_value=tmp_path)
    mocker.patch("kabukit.cli.cache.get_cache_dir", return_value=tmp_path)
    return tmp_path
