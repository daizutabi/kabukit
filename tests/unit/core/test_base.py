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
    assert_frame_equal(Base(data).data, data)


class Derived(Base):
    pass


@patch("kabukit.core.base.user_cache_dir", return_value="cache")
@pytest.mark.parametrize(("cls", "name"), [(Base, "base"), (Derived, "derived")])
def test_data_dir(user_cache_dir: MagicMock, cls: type[Base], name: str) -> None:
    assert cls.data_dir() == Path("cache") / name
    user_cache_dir.assert_called_once_with("kabukit")


@patch("kabukit.core.base.datetime")
def test_write(mock_datetime: MagicMock, data: DataFrame, tmp_path: Path) -> None:
    mock_datetime.datetime.today.return_value = datetime.datetime(2023, 10, 27)  # noqa: DTZ001

    with patch.object(Base, "data_dir", return_value=tmp_path):
        path = Base(data).write()
        assert path == tmp_path / "20231027.parquet"
        assert path.exists()
        assert_frame_equal(pl.read_parquet(path), data)


def test_read(data: DataFrame, tmp_path: Path) -> None:
    path1 = tmp_path / "20231026.parquet"
    path2 = tmp_path / "20231027.parquet"
    df1 = DataFrame({"A": [1]})
    df2 = data
    df1.write_parquet(path1)
    df2.write_parquet(path2)

    with patch.object(Base, "data_dir", return_value=tmp_path):
        base = Base.read()
        assert isinstance(base, Base)
        assert_frame_equal(base.data, df2)

        base = Base.read(path="20231026.parquet")
        assert isinstance(base, Base)
        assert_frame_equal(base.data, df1)

        with patch.object(Derived, "data_dir", return_value=tmp_path):
            derived = Derived.read()
            assert isinstance(derived, Derived)
            assert_frame_equal(derived.data, df2)


def test_read_file_not_found(tmp_path: Path) -> None:
    with (
        patch.object(Base, "data_dir", return_value=tmp_path),
        pytest.raises(FileNotFoundError, match=f"No data found in {tmp_path}"),
    ):
        Base.read()
