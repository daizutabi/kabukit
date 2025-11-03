from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl
import pytest
from polars.testing import assert_frame_equal
from typer.testing import CliRunner

from kabukit.cli.app import app

from .conftest import MOCK_DF

if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture


pytestmark = pytest.mark.integration

runner = CliRunner()


@pytest.fixture
def mock_get_shares(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jpx.batch.get_shares",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


def get_cache_files(cache_dir: Path) -> list[Path]:
    return list(cache_dir.joinpath("jpx", "shares").glob("*.parquet"))


def test_get_shares(
    mock_get_shares: AsyncMock,
    mock_cache_dir: Path,
    mocker: MockerFixture,
) -> None:
    result = runner.invoke(app, ["get", "shares"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    assert "上場株式数を" in result.stdout

    mock_get_shares.assert_called_once_with(progress=mocker.ANY, max_items=None)

    cache_files = get_cache_files(mock_cache_dir)
    assert len(cache_files) == 1
    assert_frame_equal(pl.read_parquet(cache_files[0]), MOCK_DF)
