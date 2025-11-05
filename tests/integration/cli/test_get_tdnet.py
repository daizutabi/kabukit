from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal
from typer.testing import CliRunner

from kabukit.cli.app import app
from kabukit.utils.datetime import today

from .conftest import MOCK_DATE, MOCK_DATE_OBJ, MOCK_DF

if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture


pytestmark = pytest.mark.integration

runner = CliRunner()


@pytest.fixture
def mock_get_tdnet(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.tdnet.fetcher.get_list",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


def get_cache_files(cache_dir: Path) -> list[Path]:
    return list(cache_dir.joinpath("tdnet", "list").glob("*.parquet"))


def test_get_tdnet(mock_get_tdnet: AsyncMock, mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "tdnet"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_tdnet.assert_called_once_with(today(), progress=None, max_items=None)

    assert not get_cache_files(mock_cache_dir)


def test_get_tdnet_date(mock_get_tdnet: AsyncMock, mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "tdnet", MOCK_DATE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_tdnet.assert_called_once_with(MOCK_DATE_OBJ, progress=None, max_items=None)

    assert not get_cache_files(mock_cache_dir)


def test_get_tdnet_all(
    mock_get_tdnet: AsyncMock,
    mock_cache_dir: Path,
    mocker: MockerFixture,
) -> None:
    result = runner.invoke(app, ["get", "tdnet", "--all"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    assert "書類一覧を" in result.stdout

    mock_get_tdnet.assert_called_once_with(None, progress=mocker.ANY, max_items=None)

    cache_files = get_cache_files(mock_cache_dir)
    assert len(cache_files) == 1
    assert_frame_equal(pl.read_parquet(cache_files[0]), MOCK_DF)
