from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from kabukit.domain.base import Base

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.fixture
def data() -> pl.DataFrame:
    return pl.DataFrame({"A": [1, 2], "B": ["x", "y"]})


def test_init(data: pl.DataFrame) -> None:
    assert_frame_equal(Base(data).data, data)


class Derived(Base):
    pass


def test_data_dir(mocker: MockerFixture) -> None:
    mocker.patch.object(Derived, "__module__", "kabukit.domain.jquants.derived")
    mocker.patch(
        "kabukit.utils.config.user_cache_dir",
        return_value="cache",
    )
    assert Derived.data_dir() == Path("cache") / "jquants" / "derived"


def test_write_no_name(mocker: MockerFixture, data: pl.DataFrame) -> None:
    mocker.patch.object(Derived, "__module__", "kabukit.domain.jquants.derived")
    mock_cache_write = mocker.patch(
        "kabukit.domain.cache.write",
        return_value=Path("mocked_path.parquet"),
    )
    path = Derived(data).write()
    assert path == Path("mocked_path.parquet")
    mock_cache_write.assert_called_once_with("jquants", "derived", data, None)


def test_write_with_name(mocker: MockerFixture, data: pl.DataFrame) -> None:
    mocker.patch.object(Derived, "__module__", "kabukit.domain.jquants.derived")
    mock_cache_write = mocker.patch(
        "kabukit.domain.cache.write",
        return_value=Path("mocked_path.parquet"),
    )
    path = Derived(data).write(name="my_file")
    assert path == Path("mocked_path.parquet")
    mock_cache_write.assert_called_once_with("jquants", "derived", data, "my_file")


def test_init_from_cache(mocker: MockerFixture, data: pl.DataFrame) -> None:
    mocker.patch.object(Derived, "__module__", "kabukit.domain.jquants.derived")
    mock_cache_read = mocker.patch("kabukit.domain.cache.read", return_value=data)

    derived = Derived()
    assert isinstance(derived, Derived)
    assert_frame_equal(derived.data, data)
    mock_cache_read.assert_called_once_with("jquants", "derived", None)


def test_init_from_cache_file_not_found(mocker: MockerFixture) -> None:
    mocker.patch.object(Derived, "__module__", "kabukit.domain.jquants.derived")
    mocker.patch(
        "kabukit.domain.cache.read",
        side_effect=FileNotFoundError("No data found in mocked_cache_dir"),
    )
    with pytest.raises(FileNotFoundError, match="No data found in mocked_cache_dir"):
        Derived()


def test_filter(data: pl.DataFrame) -> None:
    expected = pl.DataFrame({"A": [1], "B": ["x"]})
    assert_frame_equal(Derived(data).filter(pl.col("A") == 1).data, expected)
