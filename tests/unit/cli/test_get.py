from unittest.mock import AsyncMock, MagicMock

import pytest
import tqdm.asyncio
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from kabukit.cli.app import app

from .conftest import MOCK_CODE, MOCK_DF, MOCK_PATH

pytestmark = pytest.mark.unit

runner = CliRunner()


@pytest.fixture
def mock_jquants_concurrent_get_statements(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.jquants.concurrent.get_statements",
        new_callable=AsyncMock,
    )


@pytest.fixture
def mock_jquants_concurrent_get_prices(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.jquants.concurrent.get_prices", new_callable=AsyncMock)


def test_get_info_single_code(mock_get_info: AsyncMock) -> None:
    result = runner.invoke(app, ["get", "info", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_get_info.assert_awaited_once_with(MOCK_CODE)


def test_get_statements_single_code(
    mock_jquants_concurrent_get_statements: AsyncMock,
) -> None:
    mock_jquants_concurrent_get_statements.return_value = MOCK_DF
    result = runner.invoke(app, ["get", "statements", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_jquants_concurrent_get_statements.assert_awaited_once_with(
        MOCK_CODE,
        max_items=None,
        progress=None,
    )


def test_get_prices_single_code(mock_jquants_concurrent_get_prices: AsyncMock) -> None:
    mock_jquants_concurrent_get_prices.return_value = MOCK_DF
    result = runner.invoke(app, ["get", "prices", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_jquants_concurrent_get_prices.assert_awaited_once_with(
        MOCK_CODE,
        max_items=None,
        progress=None,
    )


def test_get_info_all_codes(
    mock_get_info: AsyncMock,
    MockInfo: MagicMock,  # noqa: N803
    mock_info: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "info"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_get_info.assert_awaited_once_with(None)
    MockInfo.assert_called_once_with(MOCK_DF)
    mock_info.write.assert_called_once()
    assert f"全銘柄の情報を '{MOCK_PATH}' に保存しました。" in result.stdout


def test_get_statements_all_codes(
    mock_jquants_concurrent_get_statements: AsyncMock,
    MockStatements: MagicMock,  # noqa: N803
    mock_statements: MagicMock,
) -> None:
    mock_jquants_concurrent_get_statements.return_value = MOCK_DF
    result = runner.invoke(app, ["get", "statements"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_jquants_concurrent_get_statements.assert_awaited_once_with(
        None,
        max_items=None,
        progress=tqdm.asyncio.tqdm,
    )
    MockStatements.assert_called_once_with(MOCK_DF)
    mock_statements.write.assert_called_once()
    assert f"全銘柄の財務情報を '{MOCK_PATH}' に保存しました。" in result.stdout


def test_get_prices_all_codes(
    mock_jquants_concurrent_get_prices: AsyncMock,
    MockPrices: MagicMock,  # noqa: N803
    mock_prices: MagicMock,
) -> None:
    mock_jquants_concurrent_get_prices.return_value = MOCK_DF
    result = runner.invoke(app, ["get", "prices"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_jquants_concurrent_get_prices.assert_awaited_once_with(
        None,
        max_items=None,
        progress=tqdm.asyncio.tqdm,
    )
    MockPrices.assert_called_once_with(MOCK_DF)
    mock_prices.write.assert_called_once()
    assert f"全銘柄の株価情報を '{MOCK_PATH}' に保存しました。" in result.stdout


def test_get_entries(
    mock_get_entries: AsyncMock,
    MockEntries: MagicMock,  # noqa: N803
    mock_entries: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "entries"])

    assert result.exit_code == 0
    mock_get_entries.assert_awaited_once_with(
        None,
        years=10,
        progress=tqdm.asyncio.tqdm,
        max_items=None,
    )
    MockEntries.assert_called_once_with(MOCK_DF)
    mock_entries.write.assert_called_once()
    assert f"書類一覧を '{MOCK_PATH}' に保存しました。" in result.stdout


def test_get_entries_with_date(
    mock_get_entries: AsyncMock,
    MockEntries: MagicMock,  # noqa: N803
) -> None:
    MOCK_DATE = "2023-01-01"  # noqa: N806
    result = runner.invoke(app, ["get", "entries", MOCK_DATE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_get_entries.assert_awaited_once_with(
        MOCK_DATE,
        years=10,
        progress=None,
        max_items=None,
    )
    MockEntries.assert_not_called()


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
def mock_cli_entries(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.cli.get.entries", new_callable=AsyncMock)


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
    mock_cli_entries: AsyncMock,
    quiet: list[str],
) -> None:
    result = runner.invoke(app, ["get", "all", *quiet])

    assert result.exit_code == 0
    q = bool(quiet)
    mock_cli_info.assert_awaited_once_with(None, quiet=q)
    mock_cli_statements.assert_awaited_once_with(None, quiet=q, max_items=None)
    mock_cli_prices.assert_awaited_once_with(None, quiet=q, max_items=None)
    mock_cli_entries.assert_awaited_once_with(quiet=q, max_items=None)


def test_get_statements_interrupt(
    mock_jquants_concurrent_get_statements: AsyncMock,
) -> None:
    mock_jquants_concurrent_get_statements.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "statements"])

    assert result.exit_code == 130
    mock_jquants_concurrent_get_statements.assert_awaited_once_with(
        None,
        max_items=None,
        progress=tqdm.asyncio.tqdm,
    )


def test_get_prices_interrupt(
    mock_jquants_concurrent_get_prices: AsyncMock,
) -> None:
    mock_jquants_concurrent_get_prices.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "prices"])

    assert result.exit_code == 130
    mock_jquants_concurrent_get_prices.assert_awaited_once_with(
        None,
        max_items=None,
        progress=tqdm.asyncio.tqdm,
    )


def test_get_entries_interrupt(mock_get_entries: AsyncMock) -> None:
    mock_get_entries.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "entries"])

    assert result.exit_code == 130
    mock_get_entries.assert_awaited_once_with(
        None,
        years=10,
        progress=tqdm.asyncio.tqdm,
        max_items=None,
    )
