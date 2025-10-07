from unittest.mock import AsyncMock, MagicMock

import pytest
import tqdm.asyncio
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from kabukit.cli.app import app

from .conftest import MOCK_CODE, MOCK_DF, MOCK_LIST_DF, MOCK_PATH

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
    mock_fetch_all: AsyncMock,
    MockStatements: MagicMock,  # noqa: N803
    mock_statements: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "statements"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_fetch_all.assert_awaited_once_with("statements", progress=tqdm.asyncio.tqdm)
    MockStatements.assert_called_once_with(MOCK_DF)
    mock_statements.write.assert_called_once()
    assert f"全銘柄の財務情報を '{MOCK_PATH}' に保存しました。" in result.stdout


def test_get_prices_all_codes(
    mock_fetch_all: AsyncMock,
    MockPrices: MagicMock,  # noqa: N803
    mock_prices: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "prices"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_fetch_all.assert_awaited_once_with(
        "prices",
        max_concurrency=8,
        progress=tqdm.asyncio.tqdm,
    )
    MockPrices.assert_called_once_with(MOCK_DF)
    mock_prices.write.assert_called_once()
    assert f"全銘柄の株価情報を '{MOCK_PATH}' に保存しました。" in result.stdout


def test_get_list(
    mock_fetch_list: AsyncMock,
    MockList: MagicMock,  # noqa: N803
    mock_list: MagicMock,
) -> None:
    result = runner.invoke(app, ["get", "list"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_fetch_list.assert_awaited_once_with(years=10, progress=tqdm.asyncio.tqdm)
    MockList.assert_called_once_with(MOCK_DF)
    mock_list.write.assert_called_once()
    assert f"報告書一覧を '{MOCK_PATH}' に保存しました。" in result.stdout


def test_get_reports(
    mock_fetch_csv: AsyncMock,
    MockReports: MagicMock,  # noqa: N803
    mock_reports: MagicMock,
    MockList: MagicMock,  # noqa: N803
    mocker: MockerFixture,
) -> None:
    mock_read_instance = mocker.MagicMock()
    mock_read_instance.data = MOCK_LIST_DF
    MockList.read.return_value = mock_read_instance

    result = runner.invoke(app, ["get", "reports"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout

    doc_ids = mock_fetch_csv.call_args[0][0]
    assert sorted(doc_ids.to_list()) == ["doc1", "doc2"]

    MockReports.assert_called_once_with(MOCK_DF)
    mock_reports.write.assert_called_once()
    assert f"報告書を '{MOCK_PATH}' に保存しました。" in result.stdout


def test_get_reports_file_not_found(
    mocker: MockerFixture,
    MockList: MagicMock,  # noqa: N803
    mock_cli_list: AsyncMock,
    mock_fetch_csv: AsyncMock,
    MockReports: MagicMock,  # noqa: N803
    mock_reports: MagicMock,
) -> None:
    mock_read_instance = mocker.MagicMock()
    mock_read_instance.data = MOCK_LIST_DF
    MockList.read.side_effect = [
        FileNotFoundError,
        mock_read_instance,
    ]

    result = runner.invoke(app, ["get", "reports"])

    assert result.exit_code == 0
    mock_cli_list.assert_awaited_once_with()

    assert MockList.read.call_count == 2

    doc_ids = mock_fetch_csv.call_args[0][0]
    assert sorted(doc_ids.to_list()) == ["doc1", "doc2"]

    MockReports.assert_called_once_with(MOCK_DF)
    mock_reports.write.assert_called_once()
    assert f"報告書を '{MOCK_PATH}' に保存しました。" in result.stdout


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
def mock_cli_list(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.cli.get.list_", new_callable=AsyncMock)


@pytest.fixture
def mock_cli_reports(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.cli.get.reports", new_callable=AsyncMock)


def test_get_all_single_code(
    mock_cli_info: AsyncMock,
    mock_cli_statements: AsyncMock,
    mock_cli_prices: AsyncMock,
) -> None:
    result = runner.invoke(app, ["get", "all", MOCK_CODE])

    assert result.exit_code == 0
    mock_cli_info.assert_awaited_once_with(MOCK_CODE)
    mock_cli_statements.assert_awaited_once_with(MOCK_CODE)
    mock_cli_prices.assert_awaited_once_with(MOCK_CODE)


def test_get_all_all_codes(
    mock_cli_info: AsyncMock,
    mock_cli_statements: AsyncMock,
    mock_cli_prices: AsyncMock,
    mock_cli_list: AsyncMock,
    mock_cli_reports: AsyncMock,
) -> None:
    result = runner.invoke(app, ["get", "all"])

    assert result.exit_code == 0
    mock_cli_info.assert_awaited_once_with(None)
    mock_cli_statements.assert_awaited_once_with(None)
    mock_cli_prices.assert_awaited_once_with(None)
    mock_cli_list.assert_awaited_once_with()
    mock_cli_reports.assert_awaited_once_with()


def test_get_statements_interrupt(mock_fetch_all: AsyncMock) -> None:
    mock_fetch_all.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "statements"])

    assert result.exit_code == 1
    assert "中断しました" in result.stdout
    mock_fetch_all.assert_awaited_once_with("statements", progress=tqdm.asyncio.tqdm)


def test_get_list_interrupt(mock_fetch_list: AsyncMock) -> None:
    mock_fetch_list.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "list"])

    assert result.exit_code == 1
    assert "中断しました" in result.stdout
    mock_fetch_list.assert_awaited_once_with(years=10, progress=tqdm.asyncio.tqdm)


def test_get_reports_interrupt(
    mock_fetch_csv: AsyncMock,
    MockList: MagicMock,  # noqa: N803
    mocker: MockerFixture,
) -> None:
    mock_read_instance = mocker.MagicMock()
    mock_read_instance.data = MOCK_LIST_DF
    MockList.read.return_value = mock_read_instance
    mock_fetch_csv.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["get", "reports"])

    assert result.exit_code == 1
    assert "中断しました" in result.stdout
    doc_ids = mock_fetch_csv.call_args[0][0]
    assert sorted(doc_ids.to_list()) == ["doc1", "doc2"]
