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
def mock_get_edinet_list(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.edinet.concurrent.get_list",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


def test_get_edinet_list_without_date(
    mock_get_edinet_list: AsyncMock,
    mock_cache_dir: Path,
    mocker: MockerFixture,
) -> None:
    result = runner.invoke(app, ["get", "edinet"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    assert "書類一覧を" in result.stdout

    mock_get_edinet_list.assert_called_once_with(
        None,
        years=10,
        progress=mocker.ANY,
        max_items=None,
    )
    path = next(mock_cache_dir.joinpath("edinet", "list").glob("*.parquet"))
    assert_frame_equal(pl.read_parquet(path), MOCK_DF)
