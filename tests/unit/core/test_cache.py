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


def test_glob_with_group(mocker: MockerFixture, tmp_path: Path) -> None:
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

    result = glob(group="test")
    assert set(result) == {file1, file2, file3}
    mock_get_cache_dir.assert_called_once()


def test_glob_no_group(mocker: MockerFixture, tmp_path: Path) -> None:
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

    result = glob(group="test")
    assert list(result) == []
    mock_get_cache_dir.assert_called_once()


def test_get_cache_filepath_with_nonexistent_name(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    from kabukit.core.cache import _get_cache_filepath

    mock_get_cache_dir = mocker.patch("kabukit.core.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    with pytest.raises(FileNotFoundError, match="File not found:"):
        _get_cache_filepath(group="test", name="non_existent")


def test_get_cache_filepath_with_name(
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

    result = _get_cache_filepath(group="test", name="rel_file")
    assert result == abs_path_file
    mock_get_cache_dir.assert_called_once()


def test_get_cache_filepath_no_name_latest_file(
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

    result = _get_cache_filepath(group="test")
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
        _get_cache_filepath(group="test")
    mock_get_cache_dir.assert_called_once()


def test_read(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.core.cache import read

    mock_get_cache_dir = mocker.patch("kabukit.core.cache.get_cache_dir")
    mock_get_cache_dir.return_value = tmp_path

    cache_dir = tmp_path / "test"
    cache_dir.mkdir()

    data = DataFrame({"A": [1, 2], "B": ["x", "y"]})
    data.write_parquet(cache_dir / "my_file.parquet")

    result = read("test", name="my_file")
    assert_frame_equal(result, data)


def test_write_no_name(mocker: MockerFixture, tmp_path: Path) -> None:
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


def test_write_with_name(mocker: MockerFixture, tmp_path: Path) -> None:
    from kabukit.core.cache import write

    mock_get_cache_dir = mocker.patch(
        "kabukit.core.cache.get_cache_dir",
        return_value=tmp_path,
    )

    data = DataFrame({"A": [1, 2], "B": ["x", "y"]})
    path = write("test", data, name="my_file")

    assert path.exists()
    assert path == tmp_path / "test" / "my_file.parquet"
    assert_frame_equal(pl.read_parquet(path), data)

    mock_get_cache_dir.assert_called_once()
