from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app
from kabukit.cli.utils import CustomTqdm

from .conftest import MOCK_DF, MOCK_PATH

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit

runner = CliRunner()


@pytest.fixture
def mock_get_shares(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jpx.fetcher.get_shares",
        new_callable=AsyncMock,
        return_value=MOCK_DF,
    )


def test_get_shares_all(
    mock_get_shares: AsyncMock,
    mock_cache_write: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "shares"])

    assert result.exit_code == 0
    assert f"上場株式数を '{MOCK_PATH}' に保存しました。" in result.stdout

    mock_get_shares.assert_awaited_once_with(progress=CustomTqdm, max_items=None)
    mock_cache_write.assert_called_once_with("jpx", "shares", MOCK_DF)


def test_get_shares_interrupt(mock_get_shares: AsyncMock) -> None:
    mock_get_shares.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "shares"])

    assert result.exit_code == 130

    mock_get_shares.assert_awaited_once_with(progress=CustomTqdm, max_items=None)
