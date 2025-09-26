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
def test_get_info_single_code(Client: MagicMock) -> None:  # noqa: N803
    client = Client.return_value
    get_info = AsyncMock(return_value=MOCK_DF)
    client.__aenter__.return_value.get_info = get_info

    result = runner.invoke(app, ["get", "info", MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    get_info.assert_awaited_once_with(MOCK_CODE)


@patch("kabukit.core.info.Info")
@patch("kabukit.jquants.client.JQuantsClient")
def test_get_info_all_codes(Client: MagicMock, Info: MagicMock) -> None:  # noqa: N803
    client = Client.return_value
    get_info = AsyncMock(return_value=MOCK_DF)
    client.__aenter__.return_value.get_info = get_info
    info = Info.return_value
    info.write.return_value = "fake/path.csv"

    result = runner.invoke(app, ["get", "info"])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    get_info.assert_awaited_once_with(None)
    Info.assert_called_once_with(MOCK_DF)
    info.write.assert_called_once()
    assert "全銘柄の情報を 'fake/path.csv' に保存しました。" in result.stdout


@pytest.mark.parametrize(
    ("command", "method"),
    [
        ("statements", "get_statements"),
        ("prices", "get_prices"),
    ],
)
@patch("kabukit.jquants.client.JQuantsClient")
def test_get_single_code(Client: MagicMock, command: str, method: str) -> None:  # noqa: N803
    client = Client.return_value
    mock = AsyncMock(return_value=MOCK_DF)
    setattr(client.__aenter__.return_value, method, mock)

    result = runner.invoke(app, ["get", command, MOCK_CODE])

    assert result.exit_code == 0
    assert str(MOCK_DF) in result.stdout
    mock.assert_awaited_once_with(MOCK_CODE)


@pytest.mark.parametrize(
    ("command", "clspath", "fetch_all_kwargs", "message"),
    [
        ("statements", "kabukit.core.statements.Statements", {}, "財務情報"),
        ("prices", "kabukit.core.prices.Prices", {"max_concurrency": 8}, "株価情報"),
    ],
)
@patch("kabukit.jquants.concurrent.fetch_all")
def test_get_all_codes(
    fetch_all: AsyncMock,
    command: str,
    clspath: str,
    fetch_all_kwargs: dict[str, Any],
    message: str,
) -> None:
    fetch_all.return_value = MOCK_DF

    with patch(clspath) as cls:
        instance = cls.return_value
        instance.write.return_value = "fake/path.csv"

        result = runner.invoke(app, ["get", command])

        assert result.exit_code == 0
        assert str(MOCK_DF) in result.stdout

        fetch_all.assert_awaited_once()
        args, kwargs = fetch_all.call_args
        assert args[0] == command
        assert "progress" in kwargs
        for k, v in fetch_all_kwargs.items():
            assert kwargs[k] == v

        cls.assert_called_once_with(MOCK_DF)
        instance.write.assert_called_once()
        assert f"全銘柄の{message}を 'fake/path.csv' に保存しました。" in result.stdout


@patch("kabukit.jquants.client.JQuantsClient")
def test_get_all_single_code(Client: MagicMock) -> None:  # noqa: N803
    # setup mock
    client = Client.return_value.__aenter__.return_value
    client.get_info = AsyncMock(return_value=MOCK_DF)
    client.get_statements = AsyncMock(return_value=MOCK_DF)
    client.get_prices = AsyncMock(return_value=MOCK_DF)

    result = runner.invoke(app, ["get", "all", MOCK_CODE])

    assert result.exit_code == 0
    assert "上場銘柄一覧を取得します。" in result.stdout
    assert "財務情報を取得します。" in result.stdout
    assert "株価を取得します。" in result.stdout
    assert result.stdout.count(str(MOCK_DF)) == 3

    client.get_info.assert_awaited_once_with(MOCK_CODE)
    client.get_statements.assert_awaited_once_with(MOCK_CODE)
    client.get_prices.assert_awaited_once_with(MOCK_CODE)


@patch("kabukit.core.prices.Prices")
@patch("kabukit.core.statements.Statements")
@patch("kabukit.jquants.concurrent.fetch_all")
@patch("kabukit.core.info.Info")
@patch("kabukit.jquants.client.JQuantsClient")
def test_get_all_for_all_codes(
    Client: MagicMock,  # noqa: N803
    Info: MagicMock,  # noqa: N803
    fetch_all: AsyncMock,
    Statements: MagicMock,  # noqa: N803
    Prices: MagicMock,  # noqa: N803
) -> None:
    client = Client.return_value.__aenter__.return_value
    client.get_info = AsyncMock(return_value=MOCK_DF)
    info = Info.return_value
    info.write.return_value = "fake/info.csv"

    fetch_all.return_value = MOCK_DF
    statements = Statements.return_value
    statements.write.return_value = "fake/statements.csv"
    prices = Prices.return_value
    prices.write.return_value = "fake/prices.csv"

    result = runner.invoke(app, ["get", "all"])

    assert result.exit_code == 0
    assert "上場銘柄一覧を取得します。" in result.stdout
    assert "財務情報を取得します。" in result.stdout
    assert "株価を取得します。" in result.stdout
    assert "---" in result.stdout

    client.get_info.assert_awaited_once_with(None)
    Info.assert_called_once_with(MOCK_DF)
    info.write.assert_called_once()
    assert "全銘柄の情報を 'fake/info.csv' に保存しました。" in result.stdout

    assert fetch_all.await_count == 2

    call_args_statements = fetch_all.await_args_list[0]
    assert call_args_statements.args[0] == "statements"
    assert "progress" in call_args_statements.kwargs
    Statements.assert_called_once_with(MOCK_DF)
    statements.write.assert_called_once()
    assert "全銘柄の財務情報を 'fake/statements.csv' に保存しました。" in result.stdout

    call_args_prices = fetch_all.await_args_list[1]
    assert call_args_prices.args[0] == "prices"
    assert "progress" in call_args_prices.kwargs
    assert call_args_prices.kwargs["max_concurrency"] == 8
    Prices.assert_called_once_with(MOCK_DF)
    prices.write.assert_called_once()
    assert "全銘柄の株価情報を 'fake/prices.csv' に保存しました。" in result.stdout
