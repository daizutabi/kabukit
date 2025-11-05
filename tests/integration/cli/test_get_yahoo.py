from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal
from typer.testing import CliRunner

from kabukit.cli.app import app

from .conftest import MOCK_CODE, MOCK_DF

if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture


pytestmark = pytest.mark.integration

runner = CliRunner()


@pytest.fixture
def mock_get_yahoo(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.yahoo.fetcher.get_quote",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


def get_cache_files(cache_dir: Path) -> list[Path]:
    return list(cache_dir.joinpath("yahoo", "quote").glob("*.parquet"))


def test_get_yahoo(mock_get_yahoo: AsyncMock, mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "yahoo"])

    assert result.exit_code == 1
    assert "--all オプションを指定してください" in result.stderr

    mock_get_yahoo.assert_not_called()
    assert not get_cache_files(mock_cache_dir)


def test_get_yahoo_code(mock_get_yahoo: AsyncMock, mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "yahoo", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_yahoo.assert_called_once_with(MOCK_CODE, progress=None, max_items=None)

    assert not get_cache_files(mock_cache_dir)


def test_get_yahoo_all(
    mock_get_yahoo: AsyncMock,
    mock_cache_dir: Path,
    mocker: MockerFixture,
) -> None:
    result = runner.invoke(app, ["get", "yahoo", "--all"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    assert "銘柄情報を" in result.stdout

    mock_get_yahoo.assert_called_once_with(None, progress=mocker.ANY, max_items=None)

    cache_files = get_cache_files(mock_cache_dir)
    assert len(cache_files) == 1
    assert_frame_equal(pl.read_parquet(cache_files[0]), MOCK_DF)
