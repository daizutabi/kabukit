from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import polars as pl

from kabukit.utils.config import get_cache_dir

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from polars import DataFrame


def glob(group: str | None = None) -> Iterator[Path]:
    """Glob parquet files in the cache directory.

    Args:
        group: The name of the cache subdirectory (e.g., "info", "statements").
              If None, it globs all `*.parquet` files recursively.

    Returns:
        An iterator of Path objects for the matched parquet files.
    """
    if group is None:
        yield from get_cache_dir().glob("**/*.parquet")
    else:
        yield from get_cache_dir().joinpath(group).glob("*.parquet")


def _get_latest_filepath(group: str) -> Path:
    filenames = sorted(glob(group))

    if not filenames:
        msg = f"No data found for {group}"
        raise FileNotFoundError(msg)

    return filenames[-1]


def _get_cache_filepath(group: str, name: str | None = None) -> Path:
    if name is None:
        return _get_latest_filepath(group)

    filename = get_cache_dir() / group / f"{name}.parquet"

    if not filename.exists():
        msg = f"File not found: {filename}"
        raise FileNotFoundError(msg)

    return filename


def read(group: str, name: str | None = None) -> DataFrame:
    """Reads a polars.DataFrame directly from the cache.

    Args:
        group: The name of the cache subdirectory (e.g., "info", "statements").
        name: Optional. A specific filename (without extension) within the cache group.
              If None, the latest file in the subdirectory is read.

    Returns:
        polars.DataFrame: The DataFrame read from the cache.

    Raises:
        FileNotFoundError: If no data is found in the cache.
    """
    filepath = _get_cache_filepath(group, name)
    return pl.read_parquet(filepath)


def write(group: str, df: DataFrame, name: str | None = None) -> Path:
    """Writes a polars.DataFrame directly to the cache.

    Args:
        group: The name of the cache subdirectory (e.g., "info", "statements").
        df: The polars.DataFrame to write.
        name: Optional. The filename (without extension) for the parquet file.
              If None, a timestamp is used as the filename.

    Returns:
        Path: The path to the written Parquet file.
    """
    data_dir = get_cache_dir() / group
    data_dir.mkdir(parents=True, exist_ok=True)

    if name is None:
        name = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d")

    filename = data_dir / f"{name}.parquet"
    df.write_parquet(filename)
    return filename
