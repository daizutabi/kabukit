import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import polars as pl
import pytest
from polars import DataFrame
from polars.testing import assert_frame_equal

from kabukit.core.base import Base


@pytest.fixture
def data() -> DataFrame:
    return DataFrame({"A": [1, 2], "B": ["x", "y"]})


def test_init(data: DataFrame) -> None:
    base = Base(data)
    assert_frame_equal(base.data, data)


@patch("kabukit.core.base.user_cache_dir", return_value="cache")
def test_data_dir(user_cache_dir: MagicMock) -> None:
    assert user_cache_dir() == "cache"
    expected_path = Path("cache") / "base"
    assert Base.data_dir() == expected_path

    class Derived(Base):
        pass

    expected_derived_path = Path("cache") / "derived"
    assert Derived.data_dir() == expected_derived_path


@patch("kabukit.core.base.datetime")
def test_write(mock_datetime: MagicMock, data: DataFrame, tmp_path: Path) -> None:
    mock_datetime.datetime.today.return_value = datetime.datetime(2023, 10, 27)  # noqa: DTZ001

    with patch.object(Base, "data_dir", return_value=tmp_path):
        base_instance = Base(data=data)
        written_path = base_instance.write()

        expected_filename = tmp_path / "20231027.parquet"
        assert written_path == expected_filename
        assert expected_filename.exists()

        read_df = pl.read_parquet(expected_filename)
        assert_frame_equal(read_df, data)


def test_read(data: DataFrame, tmp_path: Path) -> None:
    path1 = tmp_path / "20231026.parquet"
    path2 = tmp_path / "20231027.parquet"
    df1 = DataFrame({"A": [1]})
    df2 = data
    df1.write_parquet(path1)
    df2.write_parquet(path2)

    with patch.object(Base, "data_dir", return_value=tmp_path):
        instance_latest = Base.read()
        assert isinstance(instance_latest, Base)
        assert_frame_equal(instance_latest.data, df2)

        instance_specific = Base.read(path="20231026.parquet")
        assert isinstance(instance_specific, Base)
        assert_frame_equal(instance_specific.data, df1)

        class Derived(Base):
            pass

        with patch.object(Derived, "data_dir", return_value=tmp_path):
            instance_derived = Derived.read()
            assert isinstance(instance_derived, Derived)
            assert_frame_equal(instance_derived.data, df2)


def test_read_file_not_found(tmp_path: Path) -> None:
    with (
        patch.object(Base, "data_dir", return_value=tmp_path),
        pytest.raises(FileNotFoundError, match=f"No data found in {tmp_path}"),
    ):
        Base.read()
