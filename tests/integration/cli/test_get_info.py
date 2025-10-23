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
def mock_get_info(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jquants.client.JQuantsClient.get_info",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


def test_get_info_with_code(mock_get_info: AsyncMock) -> None:
    result = runner.invoke(app, ["get", "info", "1234"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_info.assert_called_once_with("1234", only_common_stocks=True)


def test_get_info_without_code(mock_get_info: AsyncMock, mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "info"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    assert "全銘柄の情報を" in result.stdout

    mock_get_info.assert_called_once_with(None, only_common_stocks=True)
    path = next(mock_cache_dir.joinpath("jquants", "info").glob("*.parquet"))
    assert_frame_equal(pl.read_parquet(path), MOCK_DF)
