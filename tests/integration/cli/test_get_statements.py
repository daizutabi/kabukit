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
def mock_get_statements(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jquants.concurrent.get_statements",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


def test_get_statements_without_code(
    mock_get_statements: AsyncMock,
    mock_cache_dir: Path,
    mocker: MockerFixture,
) -> None:
    result = runner.invoke(app, ["get", "statements"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    assert "全銘柄の財務情報を" in result.stdout

    mock_get_statements.assert_called_once_with(
        None,
        max_items=None,
        progress=mocker.ANY,
    )

    path = next(mock_cache_dir.joinpath("jquants", "statements").glob("*.parquet"))
    assert_frame_equal(pl.read_parquet(path), MOCK_DF)
