from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

from .conftest import MOCK_DF, MOCK_PATH

if TYPE_CHECKING:
    from unittest.mock import AsyncMock, MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit

runner = CliRunner()


@pytest.fixture
def mock_get_calendar(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jquants.batch.get_calendar",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


def test_get_calendar(
    mock_get_calendar: AsyncMock,
    mock_cache_write: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "calendar"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    assert f"営業日カレンダーを '{MOCK_PATH}' に保存しました。" in result.stdout

    mock_get_calendar.assert_awaited_once()
    mock_cache_write.assert_called_once_with("jquants", "calendar", MOCK_DF)


def test_get_calendar_quiet(
    mock_get_calendar: AsyncMock,
    mock_cache_write: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "calendar", "--quiet"])

    assert result.exit_code == 0
    assert result.stdout == ""

    mock_get_calendar.assert_awaited_once()
    mock_cache_write.assert_called_once_with("jquants", "calendar", MOCK_DF)
