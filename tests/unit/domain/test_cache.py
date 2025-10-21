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

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


def test_glob_by_source_and_group(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.domain.cache import glob

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    test_dir = tmp_path / "jquants" / "test"
    test_dir.mkdir(parents=True)

    # Create some dummy parquet files
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

    result = list(glob(source="jquants", group="test"))
    assert result == [file2, file3, file1]
    mock_get_cache_dir.assert_called_once()


def test_glob_all_recursively(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.domain.cache import glob

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    dir1 = tmp_path / "jquants" / "dir1"
    dir2 = tmp_path / "edinet" / "dir2"
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
    mock_get_cache_dir.assert_called_once()


def test_glob_by_group_across_sources(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.domain.cache import glob

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    # Create dummy files in different sources within the same group
    (tmp_path / "jquants" / "group1").mkdir(parents=True)
    (tmp_path / "edinet" / "group1").mkdir(parents=True)
    file1 = tmp_path / "jquants" / "group1" / "file1.parquet"
    file2 = tmp_path / "edinet" / "group1" / "file2.parquet"
    file1.touch()
    file2.touch()

    base_time = int(time.time())
    os.utime(file1, (base_time + 1, base_time + 1))
    os.utime(file2, (base_time, base_time))

    result = list(glob(group="group1"))
    assert result == [file2, file1]  # Sorted by mtime
    mock_get_cache_dir.assert_called_once()


def test_glob_by_source_recursively(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.domain.cache import glob

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    # Create dummy files in different groups within the same source
    (tmp_path / "jquants" / "group1").mkdir(parents=True)
    (tmp_path / "jquants" / "group2").mkdir(parents=True)
    file1 = tmp_path / "jquants" / "group1" / "file1.parquet"
    file2 = tmp_path / "jquants" / "group2" / "file2.parquet"
    file1.touch()
    file2.touch()

    base_time = int(time.time())
    os.utime(file1, (base_time + 1, base_time + 1))
    os.utime(file2, (base_time, base_time))

    result = list(glob(source="jquants"))
    assert result == [file2, file1]  # Sorted by mtime
    mock_get_cache_dir.assert_called_once()


def test_glob_returns_empty_if_no_data(tmp_path: Path, mocker: MockerFixture) -> None:
    from kabukit.domain.cache import glob

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    test_dir = tmp_path / "jquants" / "test"
    test_dir.mkdir(parents=True)

    result = glob(source="jquants", group="test")
    assert list(result) == []
    mock_get_cache_dir.assert_called_once()


def test_get_cache_filepath_with_nonexistent_name(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    from kabukit.domain.cache import _get_cache_filepath

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    with pytest.raises(FileNotFoundError, match="File not found:"):
        _get_cache_filepath(source="jquants", group="test", name="non_existent")


def test_get_cache_filepath_with_name(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    from kabukit.domain.cache import _get_cache_filepath

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    test_dir = tmp_path / "jquants" / "test"
    test_dir.mkdir(parents=True)

    abs_path_file = test_dir / "rel_file.parquet"
    abs_path_file.touch()

    result = _get_cache_filepath(source="jquants", group="test", name="rel_file")
    assert result == abs_path_file
    mock_get_cache_dir.assert_called_once()


def test_get_cache_filepath_no_name_latest_file(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    from kabukit.domain.cache import _get_cache_filepath

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    test_dir = tmp_path / "jquants" / "test"
    test_dir.mkdir(parents=True)

    # Create dummy parquet files with explicit modification times
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
    mock_get_cache_dir.assert_called_once()


def test_get_cache_filepath_no_data_found(
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    from kabukit.domain.cache import _get_cache_filepath

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    test_dir = tmp_path / "jquants" / "test"
    test_dir.mkdir(parents=True)

    with pytest.raises(FileNotFoundError, match="No data found for"):
        _get_cache_filepath(source="jquants", group="test")
    mock_get_cache_dir.assert_called_once()


def test_read(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.domain.cache import read

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    cache_dir = tmp_path / "jquants" / "test"
    cache_dir.mkdir(parents=True)

    data = pl.DataFrame({"A": [1, 2], "B": ["x", "y"]})
    data.write_parquet(cache_dir / "my_file.parquet")

    result = read("jquants", "test", name="my_file")
    assert_frame_equal(result, data)


def test_write_no_name(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.domain.cache import write

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    data = pl.DataFrame({"A": [1, 2], "B": ["x", "y"]})
    path = write("jquants", "test", data)

    assert path.exists()
    timestamp = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d")
    assert path == tmp_path / "jquants" / "test" / f"{timestamp}.parquet"
    assert_frame_equal(pl.read_parquet(path), data)

    mock_get_cache_dir.assert_called_once()


def test_write_with_name(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.domain.cache import write

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    data = pl.DataFrame({"A": [1, 2], "B": ["x", "y"]})
    path = write("jquants", "test", data, name="my_file")

    assert path.exists()
    assert path == tmp_path / "jquants" / "test" / "my_file.parquet"
    assert_frame_equal(pl.read_parquet(path), data)

    mock_get_cache_dir.assert_called_once()


def test_clean_all_cache(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.domain.cache import clean

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    # Test cleaning the entire cache
    (tmp_path / "jquants" / "group1").mkdir(parents=True)
    (tmp_path / "jquants" / "group1" / "file1.parquet").touch()
    (tmp_path / "edinet" / "group2").mkdir(parents=True)
    (tmp_path / "edinet" / "group2" / "file2.parquet").touch()

    assert tmp_path.exists()
    assert (tmp_path / "jquants" / "group1").exists()
    assert (tmp_path / "edinet" / "group2").exists()

    clean()  # Clean entire cache

    assert not tmp_path.exists()
    mock_get_cache_dir.assert_called_once()  # Called once for clean()


def test_clean_by_source_and_group(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.domain.cache import clean

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    (tmp_path / "jquants" / "group_to_remove").mkdir(parents=True)
    (tmp_path / "jquants" / "group_to_remove" / "file.parquet").touch()
    (tmp_path / "jquants" / "another_group").mkdir(parents=True)
    (tmp_path / "jquants" / "another_group" / "file.parquet").touch()

    assert (tmp_path / "jquants" / "group_to_remove").exists()
    assert (tmp_path / "jquants" / "another_group").exists()

    clean(source="jquants", group="group_to_remove")

    assert not (tmp_path / "jquants" / "group_to_remove").exists()
    # Other group should remain
    assert (tmp_path / "jquants" / "another_group").exists()
    mock_get_cache_dir.assert_called_once()  # Called once for clean(group=...)


def test_clean_only_source(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.domain.cache import clean

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    # Create a dummy source directory to be removed
    (tmp_path / "jquants" / "some_group").mkdir(parents=True)
    assert (tmp_path / "jquants").exists()

    # Call clean with only source
    clean(source="jquants")

    # Assert that the source directory is removed
    assert not (tmp_path / "jquants").exists()
    mock_get_cache_dir.assert_called_once()


def test_clean_only_group_not_supported(mocker: MockerFixture) -> None:
    from kabukit.domain.cache import clean

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")

    clean(group="group")

    mock_get_cache_dir.assert_not_called()


def test_clean_no_dir(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.domain.cache import clean

    mock_get_cache_dir = mocker.patch("kabukit.domain.cache.get_cache_dir")
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
