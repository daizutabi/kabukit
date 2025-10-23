from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx import HTTPStatusError, Request, Response
from typer.testing import CliRunner

from kabukit.cli.app import app
from kabukit.sources.edinet.client import AuthKey as EdinetAuthKey
from kabukit.sources.jquants.client import AuthKey as JQuantsAuthKey

if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import AsyncMock, MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.integration

runner = CliRunner()


@pytest.fixture
def mock_jquants_client_auth(mocker: MockerFixture) -> AsyncMock:
    """JQuantsClient.auth メソッドをモックするフィクスチャ

    JQuantsClient クラス自体はモックせず、auth メソッドだけをモックする
    これにより、CLIが JQuantsClient をインスタンス化する部分はテストされる
    """
    mock_auth = mocker.AsyncMock()
    mocker.patch("kabukit.sources.jquants.client.JQuantsClient.auth", new=mock_auth)
    return mock_auth


@pytest.fixture
def mock_get_config_value(mocker: MockerFixture) -> MagicMock:
    """kabukit.cli.auth.get_config_value をモックするフィクスチャ"""
    return mocker.patch("kabukit.cli.auth.get_config_value")


@pytest.fixture
def mock_typer_prompt(mocker: MockerFixture) -> MagicMock:
    """typer.prompt をモックするフィクスチャ"""
    return mocker.patch("typer.prompt")


@pytest.fixture(params=["jquants", "j"])
def jquants_command(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(params=["edinet", "e"])
def edinet_command(request: pytest.FixtureRequest) -> str:
    return request.param


def test_auth_jquants_saves_token_to_config(
    jquants_command: str,
    mock_config_path: Path,
    mock_jquants_client_auth: AsyncMock,
) -> None:
    """auth jquants コマンドが JQuantsClient.auth を呼び出し、トークンを保存する"""
    # JQuantsClient.auth が返すトークンを設定
    mock_jquants_client_auth.return_value = "mocked_id_token_123"

    # CLIコマンドを実行
    result = runner.invoke(
        app,
        [
            "auth",
            jquants_command,
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


def test_auth_jquants_handles_auth_failure(
    jquants_command: str,
    mock_config_path: Path,
    mock_jquants_client_auth: AsyncMock,
) -> None:
    """auth jquants コマンドが JQuantsClient.auth の認証失敗を適切に処理する"""
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
            jquants_command,
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


def test_auth_jquants_config_fallback(
    jquants_command: str,
    mock_config_path: Path,
    mock_jquants_client_auth: AsyncMock,
    mock_get_config_value: MagicMock,
) -> None:
    """auth jquants コマンドが設定ファイルから認証情報を読み込み、トークンを保存する"""
    # JQuantsClient.auth が返すトークンを設定
    mock_jquants_client_auth.return_value = "mocked_id_token_from_config"

    # get_config_value が設定ファイルから値を返すように設定
    def side_effect(key: str) -> str | None:
        if key == JQuantsAuthKey.MAILADDRESS:
            return "config@example.com"
        if key == JQuantsAuthKey.PASSWORD:
            return "config_password"
        return None

    mock_get_config_value.side_effect = side_effect

    # CLIコマンドを実行 (引数なし)
    result = runner.invoke(app, ["auth", jquants_command])

    # CLIコマンドが成功したことを確認
    assert result.exit_code == 0
    assert "J-QuantsのIDトークンを保存しました。" in result.stdout

    # JQuantsClient.auth が正しい引数で呼び出されたことを確認
    mock_jquants_client_auth.assert_awaited_once_with(
        "config@example.com",
        "config_password",
    )

    # 設定ファイルが正しく書き込まれたことを確認
    assert mock_config_path.exists()
    text = mock_config_path.read_text()
    assert f'{JQuantsAuthKey.ID_TOKEN} = "mocked_id_token_from_config"' in text
    mock_get_config_value.assert_any_call(JQuantsAuthKey.MAILADDRESS)
    mock_get_config_value.assert_any_call(JQuantsAuthKey.PASSWORD)


def test_auth_jquants_prompt_fallback(
    jquants_command: str,
    mock_config_path: Path,
    mock_jquants_client_auth: AsyncMock,
    mock_get_config_value: MagicMock,
    mock_typer_prompt: MagicMock,
) -> None:
    """auth jquants コマンドがプロンプトから認証情報を読み込み、トークンを保存する"""
    # JQuantsClient.auth が返すトークンを設定
    mock_jquants_client_auth.return_value = "mocked_id_token_from_prompt"

    # get_config_value が None を返すように設定 (プロンプトにフォールバックさせるため)
    mock_get_config_value.return_value = None

    # typer.prompt がダミーの入力を返すように設定
    mock_typer_prompt.side_effect = ["prompt@example.com", "prompt_password"]

    # CLIコマンドを実行 (引数なし)
    result = runner.invoke(app, ["auth", jquants_command])

    # CLIコマンドが成功したことを確認
    assert result.exit_code == 0
    assert "J-QuantsのIDトークンを保存しました。" in result.stdout

    # JQuantsClient.auth が正しい引数で呼び出されたことを確認
    mock_jquants_client_auth.assert_awaited_once_with(
        "prompt@example.com",
        "prompt_password",
    )

    # 設定ファイルが正しく書き込まれたことを確認
    assert mock_config_path.exists()
    text = mock_config_path.read_text()
    assert f'{JQuantsAuthKey.ID_TOKEN} = "mocked_id_token_from_prompt"' in text
    mock_get_config_value.assert_any_call(JQuantsAuthKey.MAILADDRESS)
    mock_get_config_value.assert_any_call(JQuantsAuthKey.PASSWORD)
    assert mock_typer_prompt.call_count == 2


@pytest.mark.parametrize(
    ("size_effect", "msg"),
    [(["", ""], "メールアドレス"), (["prompt@example.com", ""], "パスワード")],
)
def test_auth_jquants_prompt_fallback_error(
    jquants_command: str,
    mock_jquants_client_auth: AsyncMock,
    mock_get_config_value: MagicMock,
    mock_typer_prompt: MagicMock,
    size_effect: list[str],
    msg: str,
) -> None:
    """auth jquants コマンドがプロンプトから認証情報を読み出すが、空文字で失敗する"""
    # JQuantsClient.auth が返すトークンを設定
    mock_jquants_client_auth.return_value = "mocked_id_token_from_prompt"

    # get_config_value が None を返すように設定 (プロンプトにフォールバックさせるため)
    mock_get_config_value.return_value = None

    # typer.prompt がダミーの入力を返すように設定 (一部は空文字列)
    mock_typer_prompt.side_effect = size_effect

    # CLIコマンドを実行 (引数なし)
    result = runner.invoke(app, ["auth", jquants_command])

    # CLIコマンドが成功したことを確認
    assert result.exit_code == 1
    assert msg in result.stdout


def test_auth_edinet_saves_api_key_to_config(
    edinet_command: str,
    mock_config_path: Path,
    mock_typer_prompt: MagicMock,  # プロンプトが呼ばれないことを確認するため
) -> None:
    """auth edinet コマンドが API キーを引数で受け取り、設定ファイルに保存する"""
    # CLIコマンドを実行
    result = runner.invoke(
        app,
        ["auth", edinet_command, "--api-key", "cli_api_key_123"],
    )

    # CLIコマンドが成功したことを確認
    assert result.exit_code == 0
    assert "EDINETのAPIキーを保存しました。" in result.stdout

    # 設定ファイルが正しく書き込まれたことを確認
    assert mock_config_path.exists()
    text = mock_config_path.read_text()
    assert f'{EdinetAuthKey.API_KEY} = "cli_api_key_123"' in text
    mock_typer_prompt.assert_not_called()  # プロンプトは呼ばれない


def test_auth_edinet_always_prompts_and_overwrites(
    edinet_command: str,
    mock_config_path: Path,
    mock_get_config_value: MagicMock,
    mock_typer_prompt: MagicMock,
) -> None:
    """引数なしの場合、既存のキーがあっても常にプロンプトを表示することをテストする"""
    # 既存のキーが設定されている状況をシミュレート
    mock_get_config_value.return_value = "existing_api_key"
    # ユーザーがプロンプトに新しいキーを入力する状況をシミュレート
    mock_typer_prompt.return_value = "new_api_key_from_prompt"

    # CLIコマンドを実行（引数なし）
    result = runner.invoke(app, ["auth", edinet_command])

    # CLIコマンドが成功したことを確認
    assert result.exit_code == 0
    assert "EDINETのAPIキーを保存しました。" in result.stdout

    # プロンプトが表示されたことを確認
    mock_typer_prompt.assert_called_once_with("EDINETで取得したAPIキー")

    # 設定ファイルが新しいキーで正しく上書きされたことを確認
    assert mock_config_path.exists()
    text = mock_config_path.read_text()
    assert f'{EdinetAuthKey.API_KEY} = "new_api_key_from_prompt"' in text


def test_auth_edinet_prompt_fallback(
    edinet_command: str,
    mock_get_config_value: MagicMock,
    mock_config_path: Path,
    mock_typer_prompt: MagicMock,
) -> None:
    """引数なしかつ既存のキーがない場合、プロンプトを表示することをテストする"""
    mock_get_config_value.return_value = None  # 設定ファイルには存在しない

    # typer.prompt がダミーの入力を返すように設定
    mock_typer_prompt.side_effect = ["prompt_api_key_456"]

    # CLIコマンドを実行（引数なし）
    result = runner.invoke(app, ["auth", edinet_command])

    # CLIコマンドが成功したことを確認
    assert result.exit_code == 0
    assert "EDINETのAPIキーを保存しました。" in result.stdout

    # 設定ファイルが正しく書き込まれたことを確認
    assert mock_config_path.exists()
    text = mock_config_path.read_text()
    assert f'{EdinetAuthKey.API_KEY} = "prompt_api_key_456"' in text
    mock_typer_prompt.assert_called_once_with("EDINETで取得したAPIキー")


def test_auth_edinet_prompt_fallback_error(
    edinet_command: str,
    mock_get_config_value: MagicMock,
    mock_typer_prompt: MagicMock,
) -> None:
    """auth edinet コマンドがプロンプトからの入力が空の場合にエラーを処理する"""
    mock_get_config_value.return_value = None  # 設定ファイルには存在しない
    # typer.prompt が空文字列を返すように設定
    mock_typer_prompt.return_value = ""

    # CLIコマンドを実行（引数なし）
    result = runner.invoke(app, ["auth", edinet_command])

    # CLIコマンドが失敗したことを確認
    assert result.exit_code == 1
    assert "APIキーが入力されていません。" in result.stdout
    mock_typer_prompt.assert_called_once_with("EDINETで取得したAPIキー")


def test_auth_show_no_config_file(
    mock_config_path: Path,
) -> None:
    """auth show コマンドは設定ファイルが存在しないと設定ファイルだけを表示する"""
    # mock_config_path はデフォルトでファイルが存在しない状態をモックしている
    result = runner.invoke(app, ["auth", "show"])

    assert result.exit_code == 0
    assert result.stdout == f"設定ファイル: {mock_config_path}\n" in result.stdout


def test_auth_show_with_config_file(
    mock_config_path: Path,
) -> None:
    """auth show コマンドが設定ファイルが存在し、内容が正しく表示されることを確認する"""
    # テスト用の設定ファイルを作成
    mock_config_path.write_text("abc\n")

    # CLIコマンドを実行
    result = runner.invoke(app, ["auth", "show"])

    assert result.exit_code == 0
    assert f"設定ファイル: {mock_config_path!s}" in result.stdout
    assert "----\nabc\n----" in result.stdout
