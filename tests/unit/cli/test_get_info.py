from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

from .conftest import MOCK_CODE, MOCK_DF, MOCK_PATH

if TYPE_CHECKING:
    from unittest.mock import AsyncMock, MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit

runner = CliRunner()


@pytest.fixture
def mock_get_info(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jquants.concurrent.get_info",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


def test_get_info_with_code(mock_get_info: AsyncMock) -> None:
    result = runner.invoke(app, ["get", "info", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_info.assert_awaited_once_with(MOCK_CODE)


def test_get_info_without_code(
    mock_get_info: AsyncMock,
    mock_cache_write: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "info"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    assert f"全銘柄の情報を '{MOCK_PATH}' に保存しました。" in result.stdout

    mock_get_info.assert_awaited_once_with(None)
    mock_cache_write.assert_called_once_with("jquants", "info", MOCK_DF)
