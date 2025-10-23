from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
import tqdm.asyncio
from typer.testing import CliRunner

from kabukit.cli.app import app

from .conftest import MOCK_DF, MOCK_PATH

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit

runner = CliRunner()


@pytest.fixture
def mock_get_tdnet_list(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.tdnet.concurrent.get_list",
        new_callable=AsyncMock,
        return_value=MOCK_DF,
    )


def test_get_tdnet_list_with_date(
    mock_get_tdnet_list: AsyncMock,
    mock_cache_write: MagicMock,
) -> None:
    MOCK_DATE = "2023-01-01"  # noqa: N806
    result = runner.invoke(app, ["get", "tdnet", MOCK_DATE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    mock_get_tdnet_list.assert_awaited_once_with(
        MOCK_DATE,
        progress=None,
        max_items=None,
    )
    mock_cache_write.assert_not_called()


def test_get_tdnet_list_without_date(
    mock_get_tdnet_list: AsyncMock,
    mock_cache_write: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "tdnet"])

    assert result.exit_code == 0
    assert f"書類一覧を '{MOCK_PATH}' に保存しました。" in result.stdout

    mock_get_tdnet_list.assert_awaited_once_with(
        None,
        progress=tqdm.asyncio.tqdm,
        max_items=None,
    )
    mock_cache_write.assert_called_once_with("tdnet", "list", MOCK_DF)


def test_get_tdnet_list_interrupt(mock_get_tdnet_list: AsyncMock) -> None:
    mock_get_tdnet_list.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "tdnet"])

    assert result.exit_code == 130

    mock_get_tdnet_list.assert_awaited_once_with(
        None,
        progress=tqdm.asyncio.tqdm,
        max_items=None,
    )
