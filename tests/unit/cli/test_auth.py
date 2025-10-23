from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import HTTPStatusError, Request, Response
from typer.testing import CliRunner

from kabukit.cli.app import app
from kabukit.sources.edinet.client import AuthKey as EdinetAuthKey
from kabukit.sources.jquants.client import AuthKey as JQuantsAuthKey

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit

runner = CliRunner()


@pytest.fixture
def mock_jquants_client(mocker: MockerFixture) -> MagicMock:
    mock_client_instance = mocker.MagicMock()
    mock_client_instance.auth = AsyncMock(return_value="dummy_id_token")
    mock_client_instance.__aenter__.return_value = mock_client_instance
    mock_client_instance.__aexit__.return_value = None
    return mocker.patch(
        "kabukit.sources.jquants.client.JQuantsClient",
        return_value=mock_client_instance,
    )


@pytest.fixture
def mock_get_config_value(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.cli.auth.get_config_value")


@pytest.fixture
def mock_save_config_key(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.cli.auth.save_config_key")


@pytest.fixture
def mock_typer_prompt(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("typer.prompt")


def test_jquants_success_cli_args(
    mock_jquants_client: MagicMock,
    mock_get_config_value: MagicMock,
    mock_save_config_key: MagicMock,
    mock_typer_prompt: MagicMock,
) -> None:
    result = runner.invoke(
        app,
        [
            "auth",
            "jquants",
            "--mailaddress",
            "cli@example.com",
            "--password",
            "cli_password",
        ],
    )

    assert result.exit_code == 0
    assert "J-QuantsのIDトークンを保存しました。" in result.stdout
    mock_jquants_client.return_value.auth.assert_awaited_once_with(
        "cli@example.com",
        "cli_password",
    )
    mock_save_config_key.assert_called_once_with(
        JQuantsAuthKey.ID_TOKEN,
        "dummy_id_token",
    )
    mock_get_config_value.assert_not_called()
    mock_typer_prompt.assert_not_called()


def test_jquants_success_config_fallback(
    mock_jquants_client: MagicMock,
    mock_get_config_value: MagicMock,
    mock_save_config_key: MagicMock,
    mock_typer_prompt: MagicMock,
) -> None:
    def side_effect(key: str) -> str | None:
        if key == JQuantsAuthKey.MAILADDRESS:
            return "config@example.com"
        if key == JQuantsAuthKey.PASSWORD:
            return "config_password"
        return None

    mock_get_config_value.side_effect = side_effect

    result = runner.invoke(app, ["auth", "jquants"])

    assert result.exit_code == 0
    assert "J-QuantsのIDトークンを保存しました。" in result.stdout
    mock_jquants_client.return_value.auth.assert_awaited_once_with(
        "config@example.com",
        "config_password",
    )
    mock_save_config_key.assert_called_once_with(
        JQuantsAuthKey.ID_TOKEN,
        "dummy_id_token",
    )
    mock_get_config_value.assert_any_call(JQuantsAuthKey.MAILADDRESS)
    mock_get_config_value.assert_any_call(JQuantsAuthKey.PASSWORD)
    mock_typer_prompt.assert_not_called()


def test_jquants_success_prompt_fallback(
    mock_jquants_client: MagicMock,
    mock_get_config_value: MagicMock,
    mock_save_config_key: MagicMock,
    mock_typer_prompt: MagicMock,
) -> None:
    mock_get_config_value.return_value = None
    mock_typer_prompt.side_effect = ["prompt@example.com", "prompt_password"]

    result = runner.invoke(app, ["auth", "jquants"])

    assert result.exit_code == 0
    assert "J-QuantsのIDトークンを保存しました。" in result.stdout
    mock_jquants_client.return_value.auth.assert_awaited_once_with(
        "prompt@example.com",
        "prompt_password",
    )
    mock_save_config_key.assert_called_once_with(
        JQuantsAuthKey.ID_TOKEN,
        "dummy_id_token",
    )
    mock_get_config_value.assert_any_call(JQuantsAuthKey.MAILADDRESS)
    mock_get_config_value.assert_any_call(JQuantsAuthKey.PASSWORD)
    assert mock_typer_prompt.call_count == 2


def test_jquants_error_empty_prompt(
    mock_jquants_client: MagicMock,
    mock_get_config_value: MagicMock,
    mock_typer_prompt: MagicMock,
) -> None:
    mock_get_config_value.return_value = None
    mock_typer_prompt.side_effect = ["", ""]

    result = runner.invoke(app, ["auth", "jquants"])

    assert result.exit_code == 1
    assert "メールアドレスが入力されていません。" in result.stdout
    mock_jquants_client.return_value.auth.assert_not_awaited()


def test_jquants_error_empty_password_prompt(
    mock_jquants_client: MagicMock,
    mock_get_config_value: MagicMock,
    mock_typer_prompt: MagicMock,
) -> None:
    mock_get_config_value.return_value = None
    mock_typer_prompt.side_effect = ["test@example.com", ""]

    result = runner.invoke(app, ["auth", "jquants"])

    assert result.exit_code == 1
    assert "パスワードが入力されていません。" in result.stdout
    mock_jquants_client.return_value.auth.assert_not_awaited()


def test_jquants_error_http_status(
    mock_jquants_client: MagicMock,
    mock_get_config_value: MagicMock,
    mock_typer_prompt: MagicMock,
) -> None:
    mock_get_config_value.return_value = None
    mock_typer_prompt.side_effect = ["prompt@example.com", "prompt_password"]
    mock_jquants_client.return_value.auth.side_effect = HTTPStatusError(
        "400 Bad Request",
        request=Request("POST", "http://example.com"),
        response=Response(400),
    )

    result = runner.invoke(app, ["auth", "jquants"])

    assert result.exit_code == 1
    assert "認証に失敗しました" in result.stdout
    mock_jquants_client.return_value.auth.assert_awaited_once()


def test_edinet_success_cli_arg(
    mock_save_config_key: MagicMock,
    mock_typer_prompt: MagicMock,
) -> None:
    result = runner.invoke(app, ["auth", "edinet", "--api-key", "cli_api_key"])

    assert result.exit_code == 0
    assert "EDINETのAPIキーを保存しました。" in result.stdout
    mock_save_config_key.assert_called_once_with(EdinetAuthKey.API_KEY, "cli_api_key")
    mock_typer_prompt.assert_not_called()


def test_edinet_always_prompts_when_no_args(
    mock_get_config_value: MagicMock,
    mock_save_config_key: MagicMock,
    mock_typer_prompt: MagicMock,
) -> None:
    """引数なしの場合、既存のキーがあっても常にプロンプトを表示することをテストする"""
    # 既存のキーが設定されている状況をシミュレート
    mock_get_config_value.return_value = "existing_api_key"
    # ユーザーがプロンプトに新しいキーを入力する状況をシミュレート
    mock_typer_prompt.return_value = "new_api_key"

    result = runner.invoke(app, ["auth", "edinet"])

    assert result.exit_code == 0
    # プロンプトが表示されたことを確認
    mock_typer_prompt.assert_called_once_with("EDINETで取得したAPIキー")
    # 新しいキーで保存関数が呼び出されたことを確認
    mock_save_config_key.assert_called_once_with(EdinetAuthKey.API_KEY, "new_api_key")
    # 出力メッセージが正しいことを確認
    assert "EDINETのAPIキーを保存しました。" in result.stdout


def test_edinet_success_prompt_fallback(
    mock_get_config_value: MagicMock,
    mock_save_config_key: MagicMock,
    mock_typer_prompt: MagicMock,
) -> None:
    mock_get_config_value.return_value = None
    mock_typer_prompt.return_value = "prompt_api_key"

    result = runner.invoke(app, ["auth", "edinet"])

    assert result.exit_code == 0
    assert "EDINETのAPIキーを保存しました。" in result.stdout
    mock_save_config_key.assert_called_once_with(
        EdinetAuthKey.API_KEY,
        "prompt_api_key",
    )
    mock_typer_prompt.assert_called_once_with("EDINETで取得したAPIキー")


def test_edinet_error_empty_prompt(
    mock_get_config_value: MagicMock,
    mock_save_config_key: MagicMock,
    mock_typer_prompt: MagicMock,
) -> None:
    mock_get_config_value.return_value = None
    mock_typer_prompt.return_value = ""

    result = runner.invoke(app, ["auth", "edinet"])

    assert result.exit_code == 1
    assert "APIキーが入力されていません。" in result.stdout
    mock_save_config_key.assert_not_called()


@pytest.fixture
def mock_get_config_path(mocker: MockerFixture, tmp_path: Path) -> MagicMock:
    mock_path = mocker.MagicMock(spec=Path)
    mock_path.exists.return_value = False
    mock_path.__str__.return_value = str(tmp_path / "config.toml")  # pyright: ignore[reportAttributeAccessIssue]
    mocker.patch("kabukit.cli.auth.get_config_path", return_value=mock_path)
    return mock_path


def test_show_no_config_file(mock_get_config_path: MagicMock, tmp_path: Path) -> None:
    mock_get_config_path.return_value = tmp_path / "config.toml"
    result = runner.invoke(app, ["auth", "show"])

    assert result.exit_code == 0
    assert f"設定ファイル: {mock_get_config_path.return_value!s}" in result.stdout
    mock_get_config_path.exists.assert_called_once()


def test_show_with_config_file(mock_get_config_path: MagicMock, tmp_path: Path) -> None:
    mock_get_config_path.return_value = tmp_path / "config.toml"
    mock_get_config_path.exists.return_value = True

    mock_get_config_path.read_text.return_value = (
        'JQUANTS_MAILADDRESS = "test@example.com"\nEDINET_API_KEY = "abc-123"'
    )

    result = runner.invoke(app, ["auth", "show"])

    assert result.exit_code == 0
    assert f"設定ファイル: {tmp_path / 'config.toml'!s}" in result.stdout
    assert "----" in result.stdout
    assert 'JQUANTS_MAILADDRESS = "test@example.com"' in result.stdout
    assert 'EDINET_API_KEY = "abc-123"' in result.stdout
    mock_get_config_path.exists.assert_called_once()
    mock_get_config_path.read_text.assert_called_once_with(encoding="utf-8")
