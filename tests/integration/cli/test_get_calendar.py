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
def mock_get_calendar(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jquants.client.JQuantsClient.get_calendar",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


def test_get_calendar(mock_get_calendar: AsyncMock, mock_cache_dir: Path) -> None:
    result = runner.invoke(app, ["get", "calendar"])

    assert result.exit_code == 0
    assert "営業日カレンダーを" in result.stdout

    mock_get_calendar.assert_awaited_once()
    path = next(mock_cache_dir.joinpath("jquants", "calendar").glob("*.parquet"))
    assert_frame_equal(pl.read_parquet(path), MOCK_DF)
