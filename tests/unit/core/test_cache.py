from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


def test_get_cache_filepath_with_absolute_path(tmp_path: Path) -> None:
    from kabukit.core.cache import _get_cache_filepath

    abs_path_file = tmp_path / "abs_file.parquet"
    abs_path_file.touch()

    result = _get_cache_filepath(name="test", path=abs_path_file)
    assert result == abs_path_file

    result = _get_cache_filepath(name="test", path=abs_path_file.as_posix())
    assert result == abs_path_file


def test_get_cache_filepath_with_nonexistent_absolute_path(tmp_path: Path) -> None:
    from kabukit.core.cache import _get_cache_filepath

    non_existent_path = tmp_path / "non_existent.parquet"

    with pytest.raises(FileNotFoundError, match="File not found:"):
        _get_cache_filepath(name="test", path=non_existent_path)


def test_get_cache_filepath_with_relative_path(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    from kabukit.core.cache import _get_cache_filepath

    mock_get_cache_dir = mocker.patch("kabukit.core.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    test_dir = tmp_path / "test"
    test_dir.mkdir()

    abs_path_file = test_dir / "rel_file.parquet"
    abs_path_file.touch()

    result = _get_cache_filepath(name="test", path="rel_file.parquet")
    assert result == abs_path_file
    mock_get_cache_dir.assert_called_once()


def test_get_cache_filepath_no_path_latest_file(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    from kabukit.core.cache import _get_cache_filepath

    mock_get_cache_dir = mocker.patch("kabukit.core.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    test_dir = tmp_path / "test"
    test_dir.mkdir()

    # Create some dummy parquet files
    (test_dir / "20230101.parquet").touch()
    (test_dir / "20230102.parquet").touch()
    (test_dir / "20230103.parquet").touch()

    result = _get_cache_filepath(name="test")
    assert result == test_dir / "20230103.parquet"
    mock_get_cache_dir.assert_called_once()


def test_get_cache_filepath_no_data_found(
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    from kabukit.core.cache import _get_cache_filepath

    mock_get_cache_dir = mocker.patch("kabukit.core.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    test_dir = tmp_path / "test"
    test_dir.mkdir()

    with pytest.raises(FileNotFoundError, match="No data found in"):
        _get_cache_filepath(name="test")
    mock_get_cache_dir.assert_called_once()
