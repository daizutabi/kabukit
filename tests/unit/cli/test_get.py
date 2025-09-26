from unittest.mock import AsyncMock, MagicMock

import pytest
import tqdm.asyncio
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from kabukit.cli.app import app
from tests.unit.conftest import MOCK_CODE, MOCK_DF, MOCK_PATH

runner = CliRunner()


def test_get_info_single_code(get_info: AsyncMock) -> None:
    result = runner.invoke(app, ["get", "info", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    get_info.assert_awaited_once_with(MOCK_CODE)


def test_get_statements_single_code(get_statements: AsyncMock) -> None:
    result = runner.invoke(app, ["get", "statements", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    get_statements.assert_awaited_once_with(MOCK_CODE)


def test_get_prices_single_code(get_prices: AsyncMock) -> None:
    result = runner.invoke(app, ["get", "prices", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    get_prices.assert_awaited_once_with(MOCK_CODE)


def test_get_info_all_codes(
    get_info: AsyncMock,
    Info: MagicMock,  # noqa: N803
    info: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "info"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    get_info.assert_awaited_once_with(None)
    Info.assert_called_once_with(MOCK_DF)
    info.write.assert_called_once()
    assert f"全銘柄の情報を '{MOCK_PATH}' に保存しました。" in result.stdout


def test_get_statements_all_codes(
    fetch_all: AsyncMock,
    Statements: MagicMock,  # noqa: N803
    statements: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "statements"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    fetch_all.assert_awaited_once_with("statements", progress=tqdm.asyncio.tqdm)
    Statements.assert_called_once_with(MOCK_DF)
    statements.write.assert_called_once()
    assert f"全銘柄の財務情報を '{MOCK_PATH}' に保存しました。" in result.stdout


def test_get_prices_all_codes(
    fetch_all: AsyncMock,
    Prices: MagicMock,  # noqa: N803
    prices: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "prices"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    fetch_all.assert_awaited_once_with(
        "prices",
        max_concurrency=8,
        progress=tqdm.asyncio.tqdm,
    )
    Prices.assert_called_once_with(MOCK_DF)
    prices.write.assert_called_once()
    assert f"全銘柄の株価情報を '{MOCK_PATH}' に保存しました。" in result.stdout


@pytest.fixture
def mock_info(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.cli.get.info", new_callable=AsyncMock)


@pytest.fixture
def mock_statements(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.cli.get.statements", new_callable=AsyncMock)


@pytest.fixture
def mock_prices(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.cli.get.prices", new_callable=AsyncMock)


def test_get_all_single_code(
    mock_info: AsyncMock,
    mock_statements: AsyncMock,
    mock_prices: AsyncMock,
) -> None:
    result = runner.invoke(app, ["get", "all", MOCK_CODE])

    assert result.exit_code == 0
    mock_info.assert_awaited_once_with(MOCK_CODE)
    mock_statements.assert_awaited_once_with(MOCK_CODE)
    mock_prices.assert_awaited_once_with(MOCK_CODE)


def test_get_all_all_codes(
    mock_info: AsyncMock,
    mock_statements: AsyncMock,
    mock_prices: AsyncMock,
) -> None:
    result = runner.invoke(app, ["get", "all"])

    assert result.exit_code == 0
    mock_info.assert_awaited_once_with(None)
    mock_statements.assert_awaited_once_with(None)
    mock_prices.assert_awaited_once_with(None)
