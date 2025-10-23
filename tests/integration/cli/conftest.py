from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

MOCK_DF = pl.DataFrame({"Date": [1, 2], "Code": [3, 4]})


@pytest.fixture
def mock_cache_dir(tmp_path: Path, mocker: MockerFixture) -> Path:
    """Create a temporary cache directory and mock get_cache_dir for tests."""
    # For integration tests, we want to mock the cache directory to a temporary path
    # to avoid polluting the actual cache and ensure test isolation.
    mocker.patch("kabukit.domain.cache.get_cache_dir", return_value=tmp_path)
    return tmp_path
