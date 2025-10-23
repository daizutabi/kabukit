from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import polars as pl
import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


MOCK_CODE = "1234"
MOCK_DATE = "20220101"
MOCK_DATE_OBJ = datetime.date(2022, 1, 1)
MOCK_DF = pl.DataFrame({"Date": [1, 2], "Code": [3, 4]})


@pytest.fixture
def mock_cache_dir(tmp_path: Path, mocker: MockerFixture) -> Path:
    """Create a temporary cache directory and mock get_cache_dir for tests."""
    # For integration tests, we want to mock the cache directory to a temporary path
    # to avoid polluting the actual cache and ensure test isolation.
    mocker.patch("kabukit.utils.config.get_cache_dir", return_value=tmp_path)
    mocker.patch("kabukit.utils.cache.get_cache_dir", return_value=tmp_path)
    return tmp_path


@pytest.fixture
def mock_config_path(mocker: MockerFixture, tmp_path: Path) -> Path:
    """設定ファイルのパスを一時的なものに隔離するフィクスチャ"""
    config_file = tmp_path / "config.toml"
    mocker.patch("kabukit.utils.config.get_config_path", return_value=config_file)
    return config_file
