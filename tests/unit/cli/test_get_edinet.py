from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app
from kabukit.cli.get import CustomTqdm

from .conftest import MOCK_DATE, MOCK_DATE_OBJ, MOCK_DF, MOCK_PATH

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit

runner = CliRunner()


@pytest.fixture
def mock_get_edinet(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.edinet.concurrent.get_list",
        new_callable=AsyncMock,
        return_value=MOCK_DF,
    )


def test_get_edinet(mock_get_edinet: AsyncMock, mock_cache_write: MagicMock) -> None:
    from kabukit.utils.datetime import today

    result = runner.invoke(app, ["get", "edinet"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_edinet.assert_awaited_once_with(
        today(),
        years=10,
        progress=None,
        max_items=None,
    )
    mock_cache_write.assert_not_called()


def test_get_edinet_date(
    mock_get_edinet: AsyncMock,
    mock_cache_write: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "edinet", MOCK_DATE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_edinet.assert_awaited_once_with(
        MOCK_DATE_OBJ,
        years=10,
        progress=None,
        max_items=None,
    )
    mock_cache_write.assert_not_called()


def test_get_edinet_all(
    mock_get_edinet: AsyncMock,
    mock_cache_write: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "edinet", "--all"])

    assert result.exit_code == 0
    assert f"書類一覧を '{MOCK_PATH}' に保存しました。" in result.stdout

    mock_get_edinet.assert_awaited_once_with(
        None,
        years=10,
        max_items=None,
        progress=CustomTqdm,
    )
    mock_cache_write.assert_called_once_with("edinet", "list", MOCK_DF)


def test_get_edinet_interrupt(mock_get_edinet: AsyncMock) -> None:
    mock_get_edinet.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "edinet", "--all"])

    assert result.exit_code == 130

    mock_get_edinet.assert_awaited_once_with(
        None,
        years=10,
        max_items=None,
        progress=CustomTqdm,
    )
