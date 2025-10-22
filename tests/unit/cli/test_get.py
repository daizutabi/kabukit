from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest
import tqdm.asyncio
from typer.testing import CliRunner

from kabukit.cli.app import app

from .conftest import MOCK_CODE, MOCK_DF, MOCK_PATH

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit

runner = CliRunner()


def test_get_info_single_code(mock_get_info: AsyncMock) -> None:
    result = runner.invoke(app, ["get", "info", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_get_info.assert_awaited_once_with(MOCK_CODE)


def test_get_statements_single_code(mock_get_statements: AsyncMock) -> None:
    mock_get_statements.return_value = MOCK_DF
    result = runner.invoke(app, ["get", "statements", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_get_statements.assert_awaited_once_with(
        MOCK_CODE,
        max_items=None,
        progress=None,
    )


def test_get_prices_single_code(mock_get_prices: AsyncMock) -> None:
    mock_get_prices.return_value = MOCK_DF
    result = runner.invoke(app, ["get", "prices", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_get_prices.assert_awaited_once_with(MOCK_CODE, max_items=None, progress=None)


def test_get_info_all_codes(
    mock_get_info: AsyncMock,
    mock_cache_write: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "info"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    assert f"全銘柄の情報を '{MOCK_PATH}' に保存しました。" in result.stdout

    mock_get_info.assert_awaited_once_with(None)
    mock_cache_write.assert_called_once_with("jquants", "info", MOCK_DF)


def test_get_statements_all_codes(
    mock_get_statements: AsyncMock,
    mock_cache_write: MagicMock,
) -> None:
    mock_get_statements.return_value = MOCK_DF
    result = runner.invoke(app, ["get", "statements"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    assert f"全銘柄の財務情報を '{MOCK_PATH}' に保存しました。" in result.stdout

    mock_get_statements.assert_awaited_once_with(
        None,
        max_items=None,
        progress=tqdm.asyncio.tqdm,
    )
    mock_cache_write.assert_called_once_with("jquants", "statements", MOCK_DF)


def test_get_prices_all_codes(
    mock_get_prices: AsyncMock,
    mock_cache_write: MagicMock,
) -> None:
    mock_get_prices.return_value = MOCK_DF
    result = runner.invoke(app, ["get", "prices"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    assert f"全銘柄の株価情報を '{MOCK_PATH}' に保存しました。" in result.stdout

    mock_get_prices.assert_awaited_once_with(
        None,
        max_items=None,
        progress=tqdm.asyncio.tqdm,
    )
    mock_cache_write.assert_called_once_with("jquants", "prices", MOCK_DF)


def test_get_edinet_list(
    mock_get_edinet_list: AsyncMock,
    mock_cache_write: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "edinet"])

    assert result.exit_code == 0
    assert f"書類一覧を '{MOCK_PATH}' に保存しました。" in result.stdout

    mock_get_edinet_list.assert_awaited_once_with(
        None,
        years=10,
        progress=tqdm.asyncio.tqdm,
        max_items=None,
    )
    mock_cache_write.assert_called_once_with("edinet", "list", MOCK_DF)


def test_get_edinet_list_with_date(
    mock_get_edinet_list: AsyncMock,
    mock_cache_write: MagicMock,
) -> None:
    MOCK_DATE = "2023-01-01"  # noqa: N806
    result = runner.invoke(app, ["get", "edinet", MOCK_DATE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_get_edinet_list.assert_awaited_once_with(
        MOCK_DATE,
        years=10,
        progress=None,
        max_items=None,
    )
    mock_cache_write.assert_not_called()


@pytest.fixture
def mock_cli_info(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.cli.get.info", new_callable=AsyncMock)


@pytest.fixture
def mock_cli_statements(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.cli.get.statements", new_callable=AsyncMock)


@pytest.fixture
def mock_cli_prices(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.cli.get.prices", new_callable=AsyncMock)


@pytest.fixture
def mock_cli_edinet(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.cli.get.edinet", new_callable=AsyncMock)


@pytest.mark.parametrize("quiet", [[], ["-q"], ["--quiet"]])
def test_get_all_single_code(
    mock_cli_info: AsyncMock,
    mock_cli_statements: AsyncMock,
    mock_cli_prices: AsyncMock,
    quiet: list[str],
) -> None:
    result = runner.invoke(app, ["get", "all", MOCK_CODE, *quiet])

    assert result.exit_code == 0
    q = bool(quiet)
    mock_cli_info.assert_awaited_once_with(MOCK_CODE, quiet=q)
    mock_cli_statements.assert_awaited_once_with(MOCK_CODE, quiet=q, max_items=None)
    mock_cli_prices.assert_awaited_once_with(MOCK_CODE, quiet=q, max_items=None)


@pytest.mark.parametrize("quiet", [[], ["-q"], ["--quiet"]])
def test_get_all_all_codes(
    mock_cli_info: AsyncMock,
    mock_cli_statements: AsyncMock,
    mock_cli_prices: AsyncMock,
    mock_cli_edinet: AsyncMock,
    quiet: list[str],
) -> None:
    result = runner.invoke(app, ["get", "all", *quiet])

    assert result.exit_code == 0
    q = bool(quiet)
    mock_cli_info.assert_awaited_once_with(None, quiet=q)
    mock_cli_statements.assert_awaited_once_with(None, quiet=q, max_items=None)
    mock_cli_prices.assert_awaited_once_with(None, quiet=q, max_items=None)
    mock_cli_edinet.assert_awaited_once_with(quiet=q, max_items=None)


def test_get_statements_interrupt(mock_get_statements: AsyncMock) -> None:
    mock_get_statements.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "statements"])

    assert result.exit_code == 130
    mock_get_statements.assert_awaited_once_with(
        None,
        max_items=None,
        progress=tqdm.asyncio.tqdm,
    )


def test_get_prices_interrupt(mock_get_prices: AsyncMock) -> None:
    mock_get_prices.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "prices"])

    assert result.exit_code == 130
    mock_get_prices.assert_awaited_once_with(
        None,
        max_items=None,
        progress=tqdm.asyncio.tqdm,
    )


def test_get_edinet_list_interrupt(mock_get_edinet_list: AsyncMock) -> None:
    mock_get_edinet_list.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "edinet"])

    assert result.exit_code == 130
    mock_get_edinet_list.assert_awaited_once_with(
        None,
        years=10,
        progress=tqdm.asyncio.tqdm,
        max_items=None,
    )
