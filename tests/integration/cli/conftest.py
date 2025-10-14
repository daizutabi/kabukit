from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


@pytest.fixture
def mock_cache_dir(tmp_path: Path, mocker: MockerFixture) -> Path:
    """Create a temporary cache directory and mock get_cache_dir."""
    # Patch the source, for general use (e.g., in `get` commands)
    mocker.patch("kabukit.utils.config.get_cache_dir", return_value=tmp_path)

    # Patch the specific import used in the `cache` command module
    mocker.patch("kabukit.cli.cache.get_cache_dir", return_value=tmp_path)

    return tmp_path


@pytest.fixture
def mock_dotenv_path(tmp_path: Path, mocker: MockerFixture) -> Path:
    """Create a temporary .env file and mock get_dotenv_path."""
    dotenv_path = tmp_path / ".env"
    mocker.patch("kabukit.utils.config.get_dotenv_path", return_value=dotenv_path)

    return dotenv_path
