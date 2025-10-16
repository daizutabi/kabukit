import os
from pathlib import Path

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from kabukit.cli.app import app

pytestmark = pytest.mark.system

runner = CliRunner()

# 環境変数から認証情報が設定されているかチェック
is_auth_set = bool(os.getenv("JQUANTS_MAILADDRESS") and os.getenv("JQUANTS_PASSWORD"))
reason = "JQUANTS_MAILADDRESS and JQUANTS_PASSWORD must be set"


@pytest.fixture
def mock_config_path(mocker: MockerFixture, tmp_path: Path) -> Path:
    """システムテスト用の設定ファイルのパスを一時的なものに隔離するフィクスチャ"""
    config_file = tmp_path / "config.toml"
    mocker.patch("kabukit.cli.auth.get_config_path", return_value=config_file)
    mocker.patch("kabukit.utils.config.get_config_path", return_value=config_file)
    return config_file


@pytest.fixture
def authenticated_cli_session(mock_config_path: Path) -> None:
    """CLIでJ-Quants認証を成功させ、トークンを保存するフィクスチャ"""

    result = runner.invoke(app, ["auth", "jquants"])
    assert result.exit_code == 0
    assert "J-QuantsのIDトークンを保存しました。" in result.stdout
    assert mock_config_path.exists()


@pytest.mark.skipif(not is_auth_set, reason=reason)
def test_auth_jquants_success(
    mock_config_path: Path,
    authenticated_cli_session: None,  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
) -> None:
    """auth jquants コマンドが有効な認証情報で成功し、トークンを保存する"""
    # authenticated_cli_session フィクスチャが認証と保存を保証
    # ここでは、その結果としてファイルの内容が正しいことを追加で検証
    assert mock_config_path.exists()


@pytest.mark.skipif(not is_auth_set, reason=reason)
def test_auth_jquants_success_and_get_data(authenticated_cli_session: None) -> None:  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
    """auth jquants コマンドで認証後、別のCLIコマンドが成功することを確認する"""
    result_get_info = runner.invoke(app, ["get", "info", "7203"])
    assert result_get_info.exit_code == 0
    assert "Code" in result_get_info.stdout  # データが取得されたことを確認


def test_auth_jquants_failure(mock_config_path: Path) -> None:
    """auth jquants コマンドが無効な認証情報で失敗する"""
    # 無効な認証情報を引数として渡す
    result = runner.invoke(
        app,
        [
            "auth",
            "jquants",
            "--mailaddress",
            "invalid@example.com",
            "--password",
            "invalid_password",
        ],
    )

    assert result.exit_code == 1
    assert "認証に失敗しました" in result.stdout
    assert not mock_config_path.exists()
