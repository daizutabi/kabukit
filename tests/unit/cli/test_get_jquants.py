from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

from .conftest import MOCK_CODE

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit

runner = CliRunner()


@pytest.fixture
def mock_cli_info(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.cli.get.info", new_callable=AsyncMock)


@pytest.fixture
def mock_cli_statements(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.cli.get.statements", new_callable=AsyncMock)


@pytest.fixture
def mock_cli_prices(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.cli.get.prices", new_callable=AsyncMock)


@pytest.mark.parametrize("quiet", [[], ["-q"], ["--quiet"]])
@pytest.mark.parametrize(("codes", "arg"), [([MOCK_CODE], MOCK_CODE), ([], None)])
def test_get_jquants_with_code(
    mock_cli_info: AsyncMock,
    mock_cli_statements: AsyncMock,
    mock_cli_prices: AsyncMock,
    quiet: list[str],
    codes: list[str],
    arg: str | None,
) -> None:
    result = runner.invoke(app, ["get", "jquants", *codes, *quiet])

    assert result.exit_code == 0

    q = bool(quiet)
    mock_cli_info.assert_awaited_once_with(arg, quiet=q)
    mock_cli_statements.assert_awaited_once_with(arg, quiet=q, max_items=None)
    mock_cli_prices.assert_awaited_once_with(arg, quiet=q, max_items=None)
