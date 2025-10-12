from unittest.mock import AsyncMock, MagicMock

import pytest
import tqdm.asyncio
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from kabukit.cli.app import app

from .conftest import MOCK_CODE, MOCK_DF, MOCK_PATH

runner = CliRunner()


def test_get_info_single_code(mock_get_info: AsyncMock) -> None:
    result = runner.invoke(app, ["get", "info", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_get_info.assert_awaited_once_with(MOCK_CODE)


def test_get_statements_single_code(mock_get_statements: AsyncMock) -> None:
    result = runner.invoke(app, ["get", "statements", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_get_statements.assert_awaited_once_with(MOCK_CODE)


def test_get_prices_single_code(mock_get_prices: AsyncMock) -> None:
    result = runner.invoke(app, ["get", "prices", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_get_prices.assert_awaited_once_with(MOCK_CODE)


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
    mock_get_all: AsyncMock,
    MockStatements: MagicMock,  # noqa: N803
    mock_statements: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "statements"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_get_all.assert_awaited_once_with("statements", progress=tqdm.asyncio.tqdm)
    MockStatements.assert_called_once_with(MOCK_DF)
    mock_statements.write.assert_called_once()
    assert f"全銘柄の財務情報を '{MOCK_PATH}' に保存しました。" in result.stdout


def test_get_prices_all_codes(
    mock_get_all: AsyncMock,
    MockPrices: MagicMock,  # noqa: N803
    mock_prices: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "prices"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_get_all.assert_awaited_once_with(
        "prices",
        max_concurrency=8,
        progress=tqdm.asyncio.tqdm,
    )
    MockPrices.assert_called_once_with(MOCK_DF)
    mock_prices.write.assert_called_once()
    assert f"全銘柄の株価情報を '{MOCK_PATH}' に保存しました。" in result.stdout


def test_get_documents(
    mock_get_documents: AsyncMock,
    MockDocuments: MagicMock,  # noqa: N803
    mock_documents: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "documents"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_get_documents.assert_awaited_once_with(years=10, progress=tqdm.asyncio.tqdm)
    MockDocuments.assert_called_once_with(MOCK_DF)
    mock_documents.write.assert_called_once()
    assert f"書類一覧を '{MOCK_PATH}' に保存しました。" in result.stdout


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
def mock_cli_documents(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.cli.get.documents", new_callable=AsyncMock)


@pytest.mark.parametrize("quiet", [[], ["-q"], ["--quiet"]])
def test_get_all_single_code(
    mock_cli_info: AsyncMock,
    mock_cli_statements: AsyncMock,
    mock_cli_prices: AsyncMock,
    quiet: list[str],
) -> None:
    result = runner.invoke(app, ["get", "all", MOCK_CODE, *quiet])

    assert result.exit_code == 0
    mock_cli_info.assert_awaited_once_with(MOCK_CODE, quiet=bool(quiet))
    mock_cli_statements.assert_awaited_once_with(MOCK_CODE, quiet=bool(quiet))
    mock_cli_prices.assert_awaited_once_with(MOCK_CODE, quiet=bool(quiet))


@pytest.mark.parametrize("quiet", [[], ["-q"], ["--quiet"]])
def test_get_all_all_codes(
    mock_cli_info: AsyncMock,
    mock_cli_statements: AsyncMock,
    mock_cli_prices: AsyncMock,
    mock_cli_documents: AsyncMock,
    quiet: list[str],
) -> None:
    result = runner.invoke(app, ["get", "all", *quiet])

    assert result.exit_code == 0
    mock_cli_info.assert_awaited_once_with(None, quiet=bool(quiet))
    mock_cli_statements.assert_awaited_once_with(None, quiet=bool(quiet))
    mock_cli_prices.assert_awaited_once_with(None, quiet=bool(quiet))
    mock_cli_documents.assert_awaited_once_with(quiet=bool(quiet))


def test_get_statements_interrupt(mock_get_all: AsyncMock) -> None:
    mock_get_all.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "statements"])

    assert result.exit_code == 1
    assert "中断しました" in result.stdout
    mock_get_all.assert_awaited_once_with("statements", progress=tqdm.asyncio.tqdm)


def test_get_documents_interrupt(mock_get_documents: AsyncMock) -> None:
    mock_get_documents.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "documents"])

    assert result.exit_code == 1
    assert "中断しました" in result.stdout
    mock_get_documents.assert_awaited_once_with(years=10, progress=tqdm.asyncio.tqdm)
