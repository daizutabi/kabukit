from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import polars as pl
import pytest
from polars import DataFrame
from polars.testing import assert_frame_equal

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


def test_glob_with_name(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.core.cache import glob

    mock_get_cache_dir = mocker.patch("kabukit.core.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    test_dir = tmp_path / "test"
    test_dir.mkdir()

    # Create some dummy parquet files
    file1 = test_dir / "20230101.parquet"
    file2 = test_dir / "20230102.parquet"
    file3 = test_dir / "20230103.parquet"
    file1.touch()
    file2.touch()
    file3.touch()

    result = glob(name="test")
    assert set(result) == {file1, file2, file3}
    mock_get_cache_dir.assert_called_once()


def test_glob_no_name(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.core.cache import glob

    mock_get_cache_dir = mocker.patch("kabukit.core.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    dir1 = tmp_path / "dir1"
    dir2 = tmp_path / "dir2"
    dir1.mkdir()
    dir2.mkdir()

    file1 = dir1 / "file1.parquet"
    file2 = dir2 / "file2.parquet"
    file1.touch()
    file2.touch()

    result = glob()
    assert set(result) == {file1, file2}
    mock_get_cache_dir.assert_called_once()


def test_glob_no_data_found(tmp_path: Path, mocker: MockerFixture) -> None:
    from kabukit.core.cache import glob

    mock_get_cache_dir = mocker.patch("kabukit.core.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    test_dir = tmp_path / "test"
    test_dir.mkdir()

    result = glob(name="test")
    assert list(result) == []
    mock_get_cache_dir.assert_called_once()


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

    with pytest.raises(FileNotFoundError, match="No data found for"):
        _get_cache_filepath(name="test")
    mock_get_cache_dir.assert_called_once()


def test_read(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.core.cache import read

    data = DataFrame({"A": [1, 2], "B": ["x", "y"]})

    mock_get_cache_filepath = mocker.patch(
        "kabukit.core.cache._get_cache_filepath",
        return_value=tmp_path,
    )

    cache_dir = tmp_path / "test"
    cache_dir.mkdir()

    data = DataFrame({"A": [1, 2], "B": ["x", "y"]})
    data.write_parquet(cache_dir / "20230101.parquet")

    result = read("test", path="20230101.parquet")
    assert_frame_equal(result, data)

    mock_get_cache_filepath.assert_called_once_with("test", "20230101.parquet")


def test_write(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.core.cache import write

    mock_get_cache_dir = mocker.patch(
        "kabukit.core.cache.get_cache_dir",
        return_value=tmp_path,
    )

    data = DataFrame({"A": [1, 2], "B": ["x", "y"]})
    path = write("test", data)

    assert path.exists()
    timestamp = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d")
    assert path == tmp_path / "test" / f"{timestamp}.parquet"
    assert_frame_equal(pl.read_parquet(path), data)

    mock_get_cache_dir.assert_called_once()
