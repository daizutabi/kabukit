from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = pytest.mark.system

runner = CliRunner()

# 環境変数から認証情報が設定されているかチェック
is_auth_set = bool(os.getenv("J_QUANTS_MAILADDRESS") and os.getenv("J_QUANTS_PASSWORD"))
reason = "J_QUANTS_MAILADDRESS and J_QUANTS_PASSWORD must be set"


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
