import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import polars as pl
import pytest
from polars import DataFrame
from polars.testing import assert_frame_equal
from pytest_mock import MockerFixture

from kabukit.core.base import Base


@pytest.fixture
def data() -> DataFrame:
    return DataFrame({"A": [1, 2], "B": ["x", "y"]})


def test_init(data: DataFrame) -> None:
    assert_frame_equal(Base(data).data, data)


class Derived(Base):
    pass


@pytest.mark.parametrize(("cls", "name"), [(Base, "base"), (Derived, "derived")])
def test_data_dir(mocker: MockerFixture, cls: type[Base], name: str) -> None:
    mock_user_cache_dir = mocker.patch(
        "kabukit.utils.config.user_cache_dir",
        return_value="cache",
    )
    assert cls.data_dir() == Path("cache") / name
    mock_user_cache_dir.assert_called_once_with("kabukit")


def test_write(mocker: MockerFixture, data: DataFrame, tmp_path: Path) -> None:
    mock_datetime = mocker.patch("kabukit.core.base.datetime")
    mock_datetime.datetime.now.return_value = datetime.datetime(
        2023,
        10,
        27,
        tzinfo=ZoneInfo("Asia/Tokyo"),
    )

    mocker.patch.object(Base, "data_dir", return_value=tmp_path)
    path = Base(data).write()
    assert path == tmp_path / "20231027.parquet"
    assert path.exists()
    assert_frame_equal(pl.read_parquet(path), data)


def test_read(mocker: MockerFixture, data: DataFrame, tmp_path: Path) -> None:
    path1 = tmp_path / "20231026.parquet"
    path2 = tmp_path / "20231027.parquet"
    df1 = DataFrame({"A": [1]})
    df2 = data
    df1.write_parquet(path1)
    df2.write_parquet(path2)

    mocker.patch.object(Base, "data_dir", return_value=tmp_path)
    base = Base.read()
    assert isinstance(base, Base)
    assert_frame_equal(base.data, df2)

    base = Base.read(path="20231026.parquet")
    assert isinstance(base, Base)
    assert_frame_equal(base.data, df1)

    mocker.patch.object(Derived, "data_dir", return_value=tmp_path)
    derived = Derived.read()
    assert isinstance(derived, Derived)
    assert_frame_equal(derived.data, df2)


def test_read_file_not_found(mocker: MockerFixture, tmp_path: Path) -> None:
    mocker.patch.object(Base, "data_dir", return_value=tmp_path)
    with pytest.raises(FileNotFoundError, match="No data found in"):
        Base.read()


def test_filter(data: DataFrame) -> None:
    expected = DataFrame({"A": [1], "B": ["x"]})
    assert_frame_equal(Base(data).filter(pl.col("A") == 1).data, expected)
