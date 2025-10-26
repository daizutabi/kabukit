from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal
from typer.testing import CliRunner

from kabukit.cli.app import app

from .conftest import MOCK_DATE, MOCK_DATE_OBJ, MOCK_DF

if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.integration

runner = CliRunner()


@pytest.fixture
def mock_get_edinet(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.edinet.concurrent.get_list",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


def get_cache_files(cache_dir: Path) -> list[Path]:
    return list(cache_dir.joinpath("edinet", "list").glob("*.parquet"))


def test_get_edinet(mock_get_edinet: AsyncMock, mock_cache_dir: Path) -> None:
    from kabukit.utils.datetime import today

    result = runner.invoke(app, ["get", "edinet"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_edinet.assert_called_once_with(
        today(),
        years=10,
        progress=None,
        max_items=None,
    )

    assert not get_cache_files(mock_cache_dir)


def test_get_edinet_date(mock_get_edinet: AsyncMock, mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "edinet", MOCK_DATE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_edinet.assert_called_once_with(
        MOCK_DATE_OBJ,
        years=10,
        progress=None,
        max_items=None,
    )

    assert not get_cache_files(mock_cache_dir)


def test_get_edinet_all(
    mock_get_edinet: AsyncMock,
    mock_cache_dir: Path,
    mocker: MockerFixture,
) -> None:
    result = runner.invoke(app, ["get", "edinet", "--all"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    assert "書類一覧を" in result.stdout

    mock_get_edinet.assert_called_once_with(
        None,
        years=10,
        progress=mocker.ANY,
        max_items=None,
    )

    cache_files = get_cache_files(mock_cache_dir)
    assert len(cache_files) == 1
    assert_frame_equal(pl.read_parquet(cache_files[0]), MOCK_DF)
