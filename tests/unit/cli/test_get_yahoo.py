from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app
from kabukit.cli.get import CustomTqdm

from .conftest import MOCK_CODE, MOCK_DF, MOCK_PATH

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit

runner = CliRunner()


@pytest.fixture
def mock_get_yahoo(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.yahoo.batch.get_quote",
        new_callable=AsyncMock,
        return_value=MOCK_DF,
    )


def test_get_yahoo(mock_get_yahoo: AsyncMock, mock_cache_write: MagicMock) -> None:
    result = runner.invoke(app, ["get", "yahoo"])

    assert result.exit_code == 1
    assert "--all オプションを指定してください" in result.stderr

    mock_get_yahoo.assert_not_awaited()
    mock_cache_write.assert_not_called()


def test_get_yahoo_code(mock_get_yahoo: AsyncMock, mock_cache_write: MagicMock) -> None:
    result = runner.invoke(app, ["get", "yahoo", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_yahoo.assert_awaited_once_with(MOCK_CODE, progress=None, max_items=None)
    mock_cache_write.assert_not_called()


def test_get_yahoo_all(mock_get_yahoo: AsyncMock, mock_cache_write: MagicMock) -> None:
    result = runner.invoke(app, ["get", "yahoo", "--all"])

    assert result.exit_code == 0
    assert f"銘柄情報を '{MOCK_PATH}' に保存しました。" in result.stdout

    mock_get_yahoo.assert_awaited_once_with(None, max_items=None, progress=CustomTqdm)
    mock_cache_write.assert_called_once_with("yahoo", "quote", MOCK_DF)


def test_get_yaho_interrupt(mock_get_yahoo: AsyncMock) -> None:
    mock_get_yahoo.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "yahoo", "--all"])

    assert result.exit_code == 130

    mock_get_yahoo.assert_awaited_once_with(None, max_items=None, progress=CustomTqdm)
