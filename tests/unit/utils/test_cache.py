from __future__ import annotations

import datetime
import os
import shutil
import time
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from kabukit.utils.cache import _get_cache_filepath, clean, glob, read, write

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_cache_dir(tmp_path: Path, mocker: MockerFixture) -> Path:
    """Create a temporary cache directory and mock get_cache_dir for system tests."""
    mocker.patch("kabukit.utils.cache.get_cache_dir", return_value=tmp_path)
    return tmp_path


def test_glob_by_source_and_group(mock_cache_dir: Path) -> None:
    test_dir = mock_cache_dir / "jquants" / "test"
    test_dir.mkdir(parents=True)

    file1 = test_dir / "20230101.parquet"
    file2 = test_dir / "20230102.parquet"
    file3 = test_dir / "20230103.parquet"

    file1.touch()
    file2.touch()
    file3.touch()

    base_time = int(time.time())
    os.utime(file1, (base_time + 2, base_time + 2))
    os.utime(file2, (base_time, base_time))
    os.utime(file3, (base_time + 1, base_time + 1))

    result = list(glob("jquants", "test"))
    assert result == [file2, file3, file1]


def test_glob_all_recursively(mock_cache_dir: Path) -> None:
    dir1 = mock_cache_dir / "jquants" / "dir1"
    dir2 = mock_cache_dir / "edinet" / "dir2"
    dir1.mkdir(parents=True)
    dir2.mkdir(parents=True)

    file1 = dir1 / "file1.parquet"
    file2 = dir2 / "file2.parquet"
    file1.touch()
    file2.touch()

    base_time = int(time.time())
    os.utime(file1, (base_time + 1, base_time + 1))
    os.utime(file2, (base_time, base_time))

    result = list(glob())
    assert result == [file2, file1]


def test_glob_by_group_across_sources(mock_cache_dir: Path) -> None:
    group1 = mock_cache_dir / "jquants" / "group1"
    group2 = mock_cache_dir / "edinet" / "group1"
    group1.mkdir(parents=True)
    group2.mkdir(parents=True)

    file1 = group1 / "file1.parquet"
    file2 = group2 / "file2.parquet"
    file1.touch()
    file2.touch()

    base_time = int(time.time())
    os.utime(file1, (base_time + 1, base_time + 1))
    os.utime(file2, (base_time, base_time))

    result = list(glob(group="group1"))
    assert result == [file2, file1]


def test_glob_by_source_recursively(mock_cache_dir: Path) -> None:
    group1 = mock_cache_dir / "jquants" / "group1"
    group2 = mock_cache_dir / "jquants" / "group2"
    group1.mkdir(parents=True)
    group2.mkdir(parents=True)

    file1 = group1 / "file1.parquet"
    file2 = group2 / "file2.parquet"
    file1.touch()
    file2.touch()

    base_time = int(time.time())
    os.utime(file1, (base_time + 1, base_time + 1))
    os.utime(file2, (base_time, base_time))

    result = list(glob(source="jquants"))
    assert result == [file2, file1]


def test_glob_returns_empty_if_no_data(mock_cache_dir: Path) -> None:
    test_dir = mock_cache_dir / "jquants" / "test"
    test_dir.mkdir(parents=True)

    result = glob("jquants", "test")
    assert list(result) == []


def test_get_cache_filepath_with_nonexistent_name(mock_cache_dir: Path) -> None:
    test_dir = mock_cache_dir / "jquants" / "test"
    test_dir.mkdir(parents=True)

    with pytest.raises(FileNotFoundError, match="File not found:"):
        _get_cache_filepath(source="jquants", group="test", name="non_existent")


def test_get_cache_filepath_with_name(mock_cache_dir: Path) -> None:
    test_dir = mock_cache_dir / "jquants" / "test"
    test_dir.mkdir(parents=True)

    abs_path_file = test_dir / "rel_file.parquet"
    abs_path_file.touch()

    result = _get_cache_filepath(source="jquants", group="test", name="rel_file")
    assert result == abs_path_file


def test_get_cache_filepath_no_name_latest_file(mock_cache_dir: Path) -> None:
    test_dir = mock_cache_dir / "jquants" / "test"
    test_dir.mkdir(parents=True)

    file1 = test_dir / "20230103.parquet"
    file2 = test_dir / "20230102.parquet"
    file3 = test_dir / "20230101.parquet"

    file1.touch()
    file2.touch()
    file3.touch()

    base_time = int(time.time())
    os.utime(file1, (base_time, base_time))
    os.utime(file2, (base_time + 1, base_time + 1))
    os.utime(file3, (base_time + 2, base_time + 2))

    result = _get_cache_filepath(source="jquants", group="test")
    assert result == test_dir / "20230101.parquet"


def test_get_cache_filepath_no_data_found(mock_cache_dir: Path) -> None:
    test_dir = mock_cache_dir / "jquants" / "test"
    test_dir.mkdir(parents=True)

    with pytest.raises(FileNotFoundError, match="No data found for"):
        _get_cache_filepath(source="jquants", group="test")


def test_read(mock_cache_dir: Path) -> None:
    cache_dir = mock_cache_dir / "jquants" / "test"
    cache_dir.mkdir(parents=True)

    data = pl.DataFrame({"A": [1, 2], "B": ["x", "y"]})
    data.write_parquet(cache_dir / "my_file.parquet")

    result = read("jquants", "test", name="my_file")
    assert_frame_equal(result, data)


def test_write_no_name(mock_cache_dir: Path) -> None:
    data = pl.DataFrame({"A": [1, 2], "B": ["x", "y"]})
    path = write("jquants", "test", data)

    assert path.exists()
    timestamp = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d")
    assert path == mock_cache_dir / "jquants" / "test" / f"{timestamp}.parquet"
    assert_frame_equal(pl.read_parquet(path), data)


def test_write_with_name(mock_cache_dir: Path) -> None:
    data = pl.DataFrame({"A": [1, 2], "B": ["x", "y"]})
    path = write("jquants", "test", data, name="my_file")

    assert path.exists()
    assert path == mock_cache_dir / "jquants" / "test" / "my_file.parquet"
    assert_frame_equal(pl.read_parquet(path), data)


def test_clean_all_cache(mock_cache_dir: Path) -> None:
    (mock_cache_dir / "jquants" / "group1").mkdir(parents=True)
    (mock_cache_dir / "jquants" / "group1" / "file1.parquet").touch()
    (mock_cache_dir / "edinet" / "group2").mkdir(parents=True)
    (mock_cache_dir / "edinet" / "group2" / "file2.parquet").touch()

    assert (mock_cache_dir / "jquants" / "group1").exists()
    assert (mock_cache_dir / "edinet" / "group2").exists()

    clean()  # Clean entire cache

    assert not mock_cache_dir.exists()


def test_clean_by_source_and_group(mock_cache_dir: Path) -> None:
    (mock_cache_dir / "jquants" / "group_to_remove").mkdir(parents=True)
    (mock_cache_dir / "jquants" / "group_to_remove" / "file.parquet").touch()
    (mock_cache_dir / "jquants" / "another_group").mkdir(parents=True)
    (mock_cache_dir / "jquants" / "another_group" / "file.parquet").touch()

    assert (mock_cache_dir / "jquants" / "group_to_remove").exists()
    assert (mock_cache_dir / "jquants" / "another_group").exists()

    clean("jquants", "group_to_remove")

    assert not (mock_cache_dir / "jquants" / "group_to_remove").exists()
    assert (mock_cache_dir / "jquants" / "another_group").exists()


def test_clean_only_source(mock_cache_dir: Path) -> None:
    (mock_cache_dir / "jquants" / "some_group").mkdir(parents=True)
    assert (mock_cache_dir / "jquants").exists()

    clean("jquants")

    assert not (mock_cache_dir / "jquants").exists()


def test_clean_only_group_not_supported(mocker: MockerFixture) -> None:
    mock_get_cache_dir = mocker.patch("kabukit.utils.cache.get_cache_dir")

    clean(group="group")

    mock_get_cache_dir.assert_not_called()


def test_clean_no_dir(mocker: MockerFixture, tmp_path: Path) -> None:
    mock_get_cache_dir = mocker.patch("kabukit.utils.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    # Ensure the main cache directory does not exist
    if tmp_path.exists():
        shutil.rmtree(tmp_path)
    assert not tmp_path.exists()

    # Test clean() when main cache dir doesn't exist
    clean()
    assert not tmp_path.exists()
    mock_get_cache_dir.assert_called_once()  # Called once for clean()

    # Reset mock and tmp_path for group-specific clean
    mock_get_cache_dir.reset_mock()
    mock_get_cache_dir.return_value = tmp_path
    assert not tmp_path.exists()  # Ensure it's still gone

    # Test clean(group) when the group dir doesn't exist
    clean(source="jquants", group="non_existent_group")
    assert not (tmp_path / "jquants" / "non_existent_group").exists()
    mock_get_cache_dir.assert_called_once()  # Called once for clean(group=...)
