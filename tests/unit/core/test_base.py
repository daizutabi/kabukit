from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars import DataFrame
from polars.testing import assert_frame_equal

from kabukit.core.base import Base

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


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
    mock_user_cache_dir.assert_called_once_with("kabukit", appauthor=False)


def test_write_no_name(mocker: MockerFixture, data: DataFrame) -> None:
    mock_cache_write = mocker.patch(
        "kabukit.core.cache.write",
        return_value=Path("mocked_path.parquet"),
    )
    path = Base(data).write()
    assert path == Path("mocked_path.parquet")
    mock_cache_write.assert_called_once_with("base", data, None)


def test_write_with_name(mocker: MockerFixture, data: DataFrame) -> None:
    mock_cache_write = mocker.patch(
        "kabukit.core.cache.write",
        return_value=Path("mocked_path.parquet"),
    )
    path = Base(data).write(name="my_file")
    assert path == Path("mocked_path.parquet")
    mock_cache_write.assert_called_once_with("base", data, "my_file")


def test_init_from_cache(mocker: MockerFixture, data: DataFrame) -> None:
    df1 = DataFrame({"A": [1]})
    df2 = data

    # Mock cache.read for Base class
    mock_cache_read_base = mocker.patch(
        "kabukit.core.cache.read",
        side_effect=[df2, df1],
    )

    base = Base()
    assert isinstance(base, Base)
    assert_frame_equal(base.data, df2)
    mock_cache_read_base.assert_any_call("base", None)  # Check for latest

    base = Base(name="20231026")
    assert isinstance(base, Base)
    assert_frame_equal(base.data, df1)
    mock_cache_read_base.assert_any_call("base", "20231026")

    # Mock cache.read for Derived class
    mock_cache_read_derived = mocker.patch("kabukit.core.cache.read", return_value=df2)
    derived = Derived()
    assert isinstance(derived, Derived)
    assert_frame_equal(derived.data, df2)
    mock_cache_read_derived.assert_called_once_with("derived", None)


def test_init_from_cache_file_not_found(mocker: MockerFixture) -> None:
    mocker.patch(
        "kabukit.core.cache.read",
        side_effect=FileNotFoundError("No data found in mocked_cache_dir"),
    )
    with pytest.raises(FileNotFoundError, match="No data found in mocked_cache_dir"):
        Base()


def test_filter(data: DataFrame) -> None:
    expected = DataFrame({"A": [1], "B": ["x"]})
    assert_frame_equal(Base(data).filter(pl.col("A") == 1).data, expected)
