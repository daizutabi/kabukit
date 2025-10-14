from __future__ import annotations

from typing import TYPE_CHECKING

from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

runner = CliRunner()


def test_auth_edinet(mock_dotenv_path: Path) -> None:
    result = runner.invoke(app, ["auth", "edinet"], input="test_api_key\n")
    assert result.exit_code == 0
    assert "EDINETのAPIキーを保存しました。" in result.stdout
    assert mock_dotenv_path.read_text() == "EDINET_API_KEY='test_api_key'\n"


def test_auth_jquants(mock_dotenv_path: Path, mocker: MockerFixture) -> None:
    mock_auth = mocker.patch(
        "kabukit.jquants.client.JQuantsClient.auth", return_value=None
    )
    result = runner.invoke(
        app, ["auth", "jquants"], input="test@example.com\npassword\n"
    )
    assert result.exit_code == 0
    assert "J-QuantsのIDトークンを保存しました。" in result.stdout
    mock_auth.assert_called_once_with("test@example.com", "password", save=True)
    assert mock_dotenv_path.read_text()


def test_auth_show(mock_dotenv_path: Path) -> None:
    mock_dotenv_path.write_text('TEST_KEY="test_value"\n')
    result = runner.invoke(app, ["auth", "show"])
    assert result.exit_code == 0
    assert f"設定ファイル: {mock_dotenv_path}" in result.stdout
    assert "TEST_KEY: test_value" in result.stdout
