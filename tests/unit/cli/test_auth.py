from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import HTTPStatusError, Request, Response
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from kabukit.cli.app import app

runner = CliRunner()


@pytest.mark.parametrize("command", ["jquants", "j"])
def test_jquants_success(mock_jquants_client: MagicMock, command: str) -> None:
    auth = AsyncMock()
    mock_jquants_client.__aenter__.return_value.auth = auth
    result = runner.invoke(app, ["auth", command], input="t@e.com\n123\n")
    assert result.exit_code == 0
    assert "J-QuantsのIDトークンを保存しました。" in result.stdout
    auth.assert_awaited_once_with("t@e.com", "123", save=True)


@pytest.mark.parametrize("command", ["jquants", "j"])
def test_jquants_error(mock_jquants_client: MagicMock, command: str) -> None:
    mock_jquants_client.__aenter__.return_value.auth = AsyncMock(
        side_effect=HTTPStatusError(
            "400 Bad Request",
            request=Request("POST", "http://example.com"),
            response=Response(400),
        ),
    )

    result = runner.invoke(app, ["auth", command], input="a\nb\n")
    assert result.exit_code == 1
    assert "認証に失敗しました" in result.stdout


@pytest.fixture
def mock_set_key(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.utils.config.set_key")


@pytest.mark.parametrize("command", ["edinet", "e"])
def test_edinet(mock_set_key: MagicMock, command: str) -> None:
    api_key = "my_edinet_api_key"
    result = runner.invoke(app, ["auth", command], input=f"{api_key}\n")

    assert result.exit_code == 0
    assert "EDINETのAPIキーを保存しました。" in result.stdout
    mock_set_key.assert_called_once_with("EDINET_API_KEY", api_key)


def test_show() -> None:
    result = runner.invoke(app, ["auth", "show"])
    assert result.exit_code == 0
    assert "設定ファイル: " in result.stdout


@pytest.fixture
def mock_get_dotenv_path(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.utils.config.get_dotenv_path")


def test_show_with_config(mock_get_dotenv_path: MagicMock, tmp_path: Path) -> None:
    config_path = tmp_path / ".env"
    mock_get_dotenv_path.return_value = config_path

    config_content = {
        "JQUANTS_REFRESH_TOKEN": "dummy_refresh_token",
        "EDINET_API_KEY": "dummy_api_key",
    }

    with config_path.open("w", encoding="utf-8") as f:
        f.writelines(f"{key}={value}\n" for key, value in config_content.items())

    result = runner.invoke(app, ["auth", "show"])

    assert result.exit_code == 0
    assert f"設定ファイル: {config_path}" in result.stdout
    for key, value in config_content.items():
        assert f"{key}: {value}" in result.stdout
