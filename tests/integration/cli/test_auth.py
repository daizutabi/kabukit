from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx import HTTPStatusError, Request, Response
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.integration

runner = CliRunner()


@pytest.mark.parametrize("command", ["jquants", "j"])
def test_auth_jquants(
    command: str,
    mock_dotenv_path: Path,
    mocker: MockerFixture,
) -> None:
    dummy_token = "dummy_id_token"
    mock_auth = mocker.patch(
        "kabukit.jquants.client.JQuantsClient.auth", return_value=dummy_token
    )
    result = runner.invoke(app, ["auth", command], input="test@example.com\npassword\n")
    assert result.exit_code == 0
    assert "J-QuantsのIDトークンを保存しました。" in result.stdout
    mock_auth.assert_called_once_with("test@example.com", "password")
    assert mock_dotenv_path.read_text() == f"JQUANTS_ID_TOKEN='{dummy_token}'\n"


@pytest.mark.parametrize("command", ["jquants", "j"])
def test_auth_jquants_error(command: str, mocker: MockerFixture) -> None:
    mock_post = mocker.patch(
        "kabukit.jquants.client.JQuantsClient.post",
        new_callable=mocker.AsyncMock,
    )
    mock_post.side_effect = HTTPStatusError(
        "400 Bad Request",
        request=Request("POST", "http://mock-api.com/token"),
        response=Response(400),
    )

    input_ = "invalid@example.com\ninvalid_password\n"
    result = runner.invoke(app, ["auth", command], input=input_)

    assert result.exit_code == 1
    assert "認証に失敗しました" in result.stdout
    mock_post.assert_awaited_once()


@pytest.mark.parametrize("command", ["edinet", "e"])
def test_auth_edinet(command: str, mock_dotenv_path: Path) -> None:
    result = runner.invoke(app, ["auth", command], input="test_api_key\n")
    assert result.exit_code == 0
    assert "EDINETのAPIキーを保存しました。" in result.stdout
    assert mock_dotenv_path.read_text() == "EDINET_API_KEY='test_api_key'\n"


def test_auth_show(mock_dotenv_path: Path) -> None:
    mock_dotenv_path.write_text('TEST_KEY="test_value"\n')
    result = runner.invoke(app, ["auth", "show"])
    assert result.exit_code == 0
    assert f"設定ファイル: {mock_dotenv_path}" in result.stdout
    assert "TEST_KEY: test_value" in result.stdout
