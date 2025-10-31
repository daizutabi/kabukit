from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app
from kabukit.cli.get import CustomTqdm
from kabukit.utils.datetime import today

from .conftest import MOCK_CODE, MOCK_DATE, MOCK_DATE_OBJ, MOCK_DF, MOCK_PATH

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit

runner = CliRunner()


@pytest.fixture
def mock_get_statements(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jquants.batch.get_statements",
        new_callable=AsyncMock,
    )


def test_get_statements(mock_get_statements: AsyncMock) -> None:
    mock_get_statements.return_value = MOCK_DF
    result = runner.invoke(app, ["get", "statements"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_statements.assert_awaited_once_with(
        None,
        today(),
        max_items=None,
        progress=None,
    )


def test_get_statements_with_code(mock_get_statements: AsyncMock) -> None:
    mock_get_statements.return_value = MOCK_DF
    result = runner.invoke(app, ["get", "statements", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_statements.assert_awaited_once_with(
        MOCK_CODE,
        None,
        max_items=None,
        progress=None,
    )


def test_get_statements_with_date(mock_get_statements: AsyncMock) -> None:
    mock_get_statements.return_value = MOCK_DF
    result = runner.invoke(app, ["get", "statements", MOCK_DATE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_statements.assert_awaited_once_with(
        None,
        MOCK_DATE_OBJ,
        max_items=None,
        progress=None,
    )


def test_get_statements_all(
    mock_get_statements: AsyncMock,
    mock_cache_write: MagicMock,
) -> None:
    mock_get_statements.return_value = MOCK_DF
    result = runner.invoke(app, ["get", "statements", "--all"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    assert f"全銘柄の財務情報を '{MOCK_PATH}' に保存しました。" in result.stdout

    mock_get_statements.assert_awaited_once_with(
        None,
        None,
        max_items=None,
        progress=CustomTqdm,
    )
    mock_cache_write.assert_called_once_with("jquants", "statements", MOCK_DF)


def test_get_statements_interrupt(mock_get_statements: AsyncMock) -> None:
    mock_get_statements.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "statements", "--all"])

    assert result.exit_code == 130

    mock_get_statements.assert_awaited_once_with(
        None,
        None,
        max_items=None,
        progress=CustomTqdm,
    )
