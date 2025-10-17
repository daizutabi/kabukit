from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import polars as pl

from kabukit.utils.config import get_cache_dir

if TYPE_CHECKING:
    from polars import DataFrame


def _get_cache_filepath(name: str, path: str | Path | None = None) -> Path:
    data_dir = get_cache_dir() / name

    if path:
        if isinstance(path, str):
            path = Path(path)

        if path.exists():
            return path

        filename = data_dir / path

        if not filename.exists():
            msg = f"File not found: {filename}"
            raise FileNotFoundError(msg)

        return filename

    filenames = sorted(data_dir.glob("*.parquet"))

    if not filenames:
        msg = f"No data found in {data_dir}"
        raise FileNotFoundError(msg)

    return filenames[-1]


def read(name: str, path: str | Path | None = None) -> DataFrame:
    """Reads a polars.DataFrame directly from the cache.

    Args:
        name: The name of the cache subdirectory (e.g., "info", "statements").
        path: Optional. A specific path to a Parquet file within the cache.
              If None, the latest file in the subdirectory is read.

    Returns:
        polars.DataFrame: The DataFrame read from the cache.

    Raises:
        FileNotFoundError: If no data is found in the cache.
    """
    filepath = _get_cache_filepath(name, path)
    return pl.read_parquet(filepath)


def write(name: str, df: DataFrame) -> Path:
    """Writes a polars.DataFrame directly to the cache.

    Args:
        name: The name of the cache subdirectory (e.g., "info", "statements").
        df: The polars.DataFrame to write.

    Returns:
        Path: The path to the written Parquet file.
    """
    data_dir = get_cache_dir() / name
    data_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d")
    filename = data_dir / f"{timestamp}.parquet"
    df.write_parquet(filename)
    return filename
