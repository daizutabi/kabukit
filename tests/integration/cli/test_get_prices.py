from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal
from typer.testing import CliRunner

from kabukit.cli.app import app
from kabukit.utils.datetime import today

from .conftest import MOCK_CODE, MOCK_DATE, MOCK_DATE_OBJ, MOCK_DF

if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.integration

runner = CliRunner()


@pytest.fixture
def mock_get_prices(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jquants.fetcher.get_prices",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


def get_cache_files(cache_dir: Path) -> list[Path]:
    return list(cache_dir.joinpath("jquants", "prices").glob("*.parquet"))


def test_get_prices(
    mock_get_prices: AsyncMock,
    mock_cache_dir: Path,
) -> None:
    result = runner.invoke(app, ["get", "prices"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_prices.assert_called_once_with(
        None,
        today(),
        max_items=None,
        progress=None,
    )

    assert not get_cache_files(mock_cache_dir)


def test_get_prices_with_code(
    mock_get_prices: AsyncMock,
    mock_cache_dir: Path,
) -> None:
    result = runner.invoke(app, ["get", "prices", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_prices.assert_called_once_with(
        MOCK_CODE,
        None,
        max_items=None,
        progress=None,
    )

    assert not get_cache_files(mock_cache_dir)


def test_get_prices_with_date(
    mock_get_prices: AsyncMock,
    mock_cache_dir: Path,
) -> None:
    result = runner.invoke(app, ["get", "prices", MOCK_DATE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_prices.assert_called_once_with(
        None,
        MOCK_DATE_OBJ,
        max_items=None,
        progress=None,
    )

    assert not get_cache_files(mock_cache_dir)


def test_get_prices_all(
    mock_get_prices: AsyncMock,
    mock_cache_dir: Path,
    mocker: MockerFixture,
) -> None:
    result = runner.invoke(app, ["get", "prices", "--all"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    assert "全銘柄の株価情報を" in result.stdout

    mock_get_prices.assert_called_once_with(
        None,
        None,
        max_items=None,
        progress=mocker.ANY,
    )

    cache_files = get_cache_files(mock_cache_dir)
    assert len(cache_files) == 1
    assert_frame_equal(pl.read_parquet(cache_files[0]), MOCK_DF)
