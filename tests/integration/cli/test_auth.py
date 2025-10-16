from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from httpx import HTTPStatusError, Request, Response
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from kabukit.cli.app import app
from kabukit.jquants.client import AuthKey as JQuantsAuthKey

pytestmark = pytest.mark.integration

runner = CliRunner()


@pytest.fixture
def mock_config_path(mocker: MockerFixture, tmp_path: Path) -> Path:
    """設定ファイルのパスを一時的なものに隔離するフィクスチャ"""
    config_file = tmp_path / "config.toml"
    mocker.patch("kabukit.cli.auth.get_config_path", return_value=config_file)
    mocker.patch("kabukit.utils.config.get_config_path", return_value=config_file)
    return config_file


@pytest.fixture
def mock_jquants_client_auth(mocker: MockerFixture) -> AsyncMock:
    """JQuantsClient.auth メソッドをモックするフィクスチャ

    JQuantsClient クラス自体はモックせず、auth メソッドだけをモックする
    これにより、CLIが JQuantsClient をインスタンス化する部分はテストされる
    """
    mock_auth = mocker.AsyncMock()
    mocker.patch("kabukit.jquants.client.JQuantsClient.auth", new=mock_auth)
    return mock_auth


@pytest.fixture(params=["jquants", "j"])
def command(request: pytest.FixtureRequest) -> str:
    return request.param


def test_auth_command_saves_token_to_config(
    command: str,
    mock_config_path: Path,
    mock_jquants_client_auth: AsyncMock,
) -> None:
    """auth コマンドが JQuantsClient.auth を呼び出し、返されたトークンを保存する"""
    # JQuantsClient.auth が返すトークンを設定
    mock_jquants_client_auth.return_value = "mocked_id_token_123"

    # CLIコマンドを実行
    result = runner.invoke(
        app,
        [
            "auth",
            command,
            "--mailaddress",
            "test@example.com",
            "--password",
            "password",
        ],
    )

    # CLIコマンドが成功したことを確認
    assert result.exit_code == 0
    assert "J-QuantsのIDトークンを保存しました。" in result.stdout

    # JQuantsClient.auth が正しい引数で呼び出されたことを確認
    mock_jquants_client_auth.assert_awaited_once_with("test@example.com", "password")

    # 設定ファイルが正しく書き込まれたことを確認
    assert mock_config_path.exists()
    text = mock_config_path.read_text()
    assert f'{JQuantsAuthKey.ID_TOKEN} = "mocked_id_token_123"' in text


def test_auth_command_handles_auth_failure(
    command: str,
    mock_config_path: Path,
    mock_jquants_client_auth: AsyncMock,
) -> None:
    """CLI auth コマンドが JQuantsClient.auth の認証失敗を適切に処理すること"""
    # JQuantsClient.auth が HTTPStatusError を発生させるように設定
    mock_jquants_client_auth.side_effect = HTTPStatusError(
        "401 Unauthorized",
        request=Request("POST", "http://example.com"),
        response=Response(401),
    )

    # CLIコマンドを実行
    result = runner.invoke(
        app,
        [
            "auth",
            command,
            "--mailaddress",
            "test@example.com",
            "--password",
            "password",
        ],
    )

    # CLIコマンドが失敗したことを確認
    assert result.exit_code == 1
    assert "認証に失敗しました" in result.stdout

    # JQuantsClient.auth が呼び出されたことを確認
    mock_jquants_client_auth.assert_awaited_once_with("test@example.com", "password")

    # 設定ファイルが作成されていないことを確認
    assert not mock_config_path.exists()
