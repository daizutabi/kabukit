from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from polars import DataFrame
from typer.testing import CliRunner

from kabukit.cli.app import app

runner = CliRunner()
MOCK_DF = DataFrame({"A": [1, 2], "B": [3, 4]})
MOCK_CODE = "1234"


@patch("kabukit.jquants.client.JQuantsClient")
def test_get_info_single_code(mock_client: MagicMock) -> None:
    # setup mock
    mock_instance = mock_client.return_value
    mock_instance.__aenter__.return_value.get_info = AsyncMock(return_value=MOCK_DF)

    # run command
    result = runner.invoke(app, ["get", "info", MOCK_CODE])

    # assert
    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_instance.__aenter__.return_value.get_info.assert_awaited_once_with(MOCK_CODE)


@patch("kabukit.core.info.Info")
@patch("kabukit.jquants.client.JQuantsClient")
def test_get_info_all_codes(
    mock_client: MagicMock,
    mock_info_writer: MagicMock,
) -> None:
    # setup mock
    mock_client_instance = mock_client.return_value
    mock_client_instance.__aenter__.return_value.get_info = AsyncMock(
        return_value=MOCK_DF,
    )
    mock_writer_instance = mock_info_writer.return_value
    mock_writer_instance.write.return_value = "fake/path.csv"

    # run command
    result = runner.invoke(app, ["get", "info"])

    # assert
    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock_client_instance.__aenter__.return_value.get_info.assert_awaited_once_with(None)
    mock_info_writer.assert_called_once_with(MOCK_DF)
    mock_writer_instance.write.assert_called_once()
    assert "全銘柄の情報を 'fake/path.csv' に保存しました。" in result.stdout


@pytest.mark.parametrize(
    ("command", "client_method"),
    [
        ("statements", "get_statements"),
        ("prices", "get_prices"),
    ],
)
@patch("kabukit.jquants.client.JQuantsClient")
def test_get_single_code(
    mock_client: MagicMock,
    command: str,
    client_method: str,
) -> None:
    # setup mock
    mock_instance = mock_client.return_value
    async_method_mock = AsyncMock(return_value=MOCK_DF)
    setattr(mock_instance.__aenter__.return_value, client_method, async_method_mock)

    # run command
    result = runner.invoke(app, ["get", command, MOCK_CODE])

    # assert
    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    async_method_mock.assert_awaited_once_with(MOCK_CODE)


@pytest.mark.parametrize(
    ("command", "writer_cls_path", "fetch_all_kwargs", "message"),
    [
        ("statements", "kabukit.core.statements.Statements", {}, "財務情報"),
        ("prices", "kabukit.core.prices.Prices", {"max_concurrency": 8}, "株価情報"),
    ],
)
@patch("kabukit.jquants.concurrent.fetch_all")
def test_get_all_codes(
    mock_fetch_all: AsyncMock,
    command: str,
    writer_cls_path: str,
    fetch_all_kwargs: dict[str, Any],
    message: str,
) -> None:
    with patch(writer_cls_path) as mock_writer_cls:
        # setup mock
        mock_fetch_all.return_value = MOCK_DF
        mock_writer_instance = mock_writer_cls.return_value
        mock_writer_instance.write.return_value = "fake/path.csv"

        # run command
        result = runner.invoke(app, ["get", command])

        # assert
        assert result.exit_code == 0
        assert str(MOCK_DF) in result.stdout

        mock_fetch_all.assert_awaited_once()
        args, kwargs = mock_fetch_all.call_args
        assert args[0] == command
        assert "progress" in kwargs
        for k, v in fetch_all_kwargs.items():
            assert kwargs[k] == v

        mock_writer_cls.assert_called_once_with(MOCK_DF)
        mock_writer_instance.write.assert_called_once()
        assert f"全銘柄の{message}を 'fake/path.csv' に保存しました。" in result.stdout


@patch("kabukit.jquants.client.JQuantsClient")
def test_get_all_single_code(mock_client: MagicMock) -> None:
    # setup mock
    mock_instance = mock_client.return_value.__aenter__.return_value
    mock_instance.get_info = AsyncMock(return_value=MOCK_DF)
    mock_instance.get_statements = AsyncMock(return_value=MOCK_DF)
    mock_instance.get_prices = AsyncMock(return_value=MOCK_DF)

    # run command
    result = runner.invoke(app, ["get", "all", MOCK_CODE])

    # assert
    assert result.exit_code == 0
    assert "上場銘柄一覧を取得します。" in result.stdout
    assert "財務情報を取得します。" in result.stdout
    assert "株価を取得します。" in result.stdout
    assert result.stdout.count(str(MOCK_DF)) == 3

    mock_instance.get_info.assert_awaited_once_with(MOCK_CODE)
    mock_instance.get_statements.assert_awaited_once_with(MOCK_CODE)
    mock_instance.get_prices.assert_awaited_once_with(MOCK_CODE)


@patch("kabukit.core.prices.Prices")
@patch("kabukit.core.statements.Statements")
@patch("kabukit.jquants.concurrent.fetch_all")
@patch("kabukit.core.info.Info")
@patch("kabukit.jquants.client.JQuantsClient")
def test_get_all_for_all_codes(
    mock_client: MagicMock,
    mock_info_writer: MagicMock,
    mock_fetch_all: AsyncMock,
    mock_statements_writer: MagicMock,
    mock_prices_writer: MagicMock,
) -> None:
    # setup mock for info
    mock_client_instance = mock_client.return_value.__aenter__.return_value
    mock_client_instance.get_info = AsyncMock(return_value=MOCK_DF)
    mock_info_writer_instance = mock_info_writer.return_value
    mock_info_writer_instance.write.return_value = "fake/info.csv"

    # setup mock for statements and prices
    mock_fetch_all.return_value = MOCK_DF
    mock_statements_writer_instance = mock_statements_writer.return_value
    mock_statements_writer_instance.write.return_value = "fake/statements.csv"
    mock_prices_writer_instance = mock_prices_writer.return_value
    mock_prices_writer_instance.write.return_value = "fake/prices.csv"

    # run command
    result = runner.invoke(app, ["get", "all"])

    # assert
    assert result.exit_code == 0
    assert "上場銘柄一覧を取得します。" in result.stdout
    assert "財務情報を取得します。" in result.stdout
    assert "株価を取得します。" in result.stdout
    assert "---" in result.stdout

    # assert info call
    mock_client_instance.get_info.assert_awaited_once_with(None)
    mock_info_writer.assert_called_once_with(MOCK_DF)
    mock_info_writer_instance.write.assert_called_once()
    assert "全銘柄の情報を 'fake/info.csv' に保存しました。" in result.stdout

    # assert fetch_all calls
    assert mock_fetch_all.await_count == 2

    # First call: statements
    call_args_statements = mock_fetch_all.await_args_list[0]
    assert call_args_statements.args[0] == "statements"
    assert "progress" in call_args_statements.kwargs
    mock_statements_writer.assert_called_once_with(MOCK_DF)
    mock_statements_writer_instance.write.assert_called_once()
    assert "全銘柄の財務情報を 'fake/statements.csv' に保存しました。" in result.stdout

    # Second call: prices
    call_args_prices = mock_fetch_all.await_args_list[1]
    assert call_args_prices.args[0] == "prices"
    assert "progress" in call_args_prices.kwargs
    assert call_args_prices.kwargs["max_concurrency"] == 8
    mock_prices_writer.assert_called_once_with(MOCK_DF)
    mock_prices_writer_instance.write.assert_called_once()
    assert "全銘柄の株価情報を 'fake/prices.csv' に保存しました。" in result.stdout
