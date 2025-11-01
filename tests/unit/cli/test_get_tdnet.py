from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app
from kabukit.cli.get import CustomTqdm
from kabukit.utils.datetime import today

from .conftest import MOCK_DATE, MOCK_DATE_OBJ, MOCK_DF, MOCK_PATH

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit

runner = CliRunner()


@pytest.fixture
def mock_get_tdnet(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.tdnet.batch.get_list",
        new_callable=AsyncMock,
        return_value=MOCK_DF,
    )


def test_get_tdnet(mock_get_tdnet: AsyncMock, mock_cache_write: MagicMock) -> None:
    result = runner.invoke(app, ["get", "tdnet"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_tdnet.assert_awaited_once_with(today(), progress=None, max_items=None)
    mock_cache_write.assert_not_called()


def test_get_tdnet_date(
    mock_get_tdnet: AsyncMock,
    mock_cache_write: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "tdnet", MOCK_DATE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_tdnet.assert_awaited_once_with(
        MOCK_DATE_OBJ,
        progress=None,
        max_items=None,
    )
    mock_cache_write.assert_not_called()


def test_get_tdnet_all(mock_get_tdnet: AsyncMock, mock_cache_write: MagicMock) -> None:
    result = runner.invoke(app, ["get", "tdnet", "--all"])

    assert result.exit_code == 0
    assert f"書類一覧を '{MOCK_PATH}' に保存しました。" in result.stdout

    mock_get_tdnet.assert_awaited_once_with(None, progress=CustomTqdm, max_items=None)
    mock_cache_write.assert_called_once_with("tdnet", "list", MOCK_DF)


def test_get_tdnet_code(mock_get_tdnet: AsyncMock, mock_cache_write: MagicMock) -> None:
    result = runner.invoke(app, ["get", "tdnet", "1000"])

    assert result.exit_code == 1
    assert "銘柄コードではなく日付を指定してください。" in result.stderr

    mock_get_tdnet.assert_not_awaited()
    mock_cache_write.assert_not_called()


def test_get_tdnet_interrupt(mock_get_tdnet: AsyncMock) -> None:
    mock_get_tdnet.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "tdnet", "--all"])

    assert result.exit_code == 130

    mock_get_tdnet.assert_awaited_once_with(None, progress=CustomTqdm, max_items=None)
