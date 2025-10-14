from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from kabukit.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

# pyright: reportUnusedParameter=false

pytestmark = pytest.mark.system

runner = CliRunner()


@pytest.fixture(autouse=True)
def mock_dotenv_path(tmp_path: Path, mocker: MockerFixture) -> Path:
    """Create a temporary .env file and mock get_dotenv_path."""
    dotenv_path = tmp_path / ".env"
    mocker.patch("kabukit.utils.config.get_dotenv_path", return_value=dotenv_path)
    return dotenv_path


@pytest.fixture
def jquants_credentials(mocker: MockerFixture) -> None:
    """Set J-Quants credentials from environment variables for testing."""
    # These should be set in your local .env or GitHub Secrets
    mocker.patch.dict(
        os.environ,
        {
            "JQUANTS_MAILADDRESS": os.environ.get(
                "JQUANTS_MAILADDRESS",
                "test@example.com",
            ),
            "JQUANTS_PASSWORD": os.environ.get("JQUANTS_PASSWORD", "test_password"),
        },
    )


@pytest.fixture
def edinet_api_key(mocker: MockerFixture) -> None:
    """Set EDINET API key from environment variables for testing."""
    # This should be set in your local .env or GitHub Secrets
    mocker.patch.dict(
        os.environ,
        {"EDINET_API_KEY": os.environ.get("EDINET_API_KEY", "test_edinet_api_key")},
    )


def test_auth_jquants_system(
    mock_dotenv_path: Path,
    jquants_credentials: None,  # Ensure credentials are set  # noqa: ARG001
) -> None:
    """
    System test for 'kabu auth jquants' command.
    Hits the live J-Quants authentication endpoint.
    Requires JQUANTS_MAILADDRESS and JQUANTS_PASSWORD to be set in environment.
    """
    # We don't provide input here, as the command should pick up from env vars
    # or prompt if not found. For system test, we assume env vars are set.
    result = runner.invoke(app, ["auth", "jquants"])

    assert result.exit_code == 0
    assert "J-QuantsのIDトークンを保存しました。" in result.stdout
    assert mock_dotenv_path.exists()
    assert "JQUANTS_ID_TOKEN" in mock_dotenv_path.read_text()


def test_auth_edinet_system(
    mock_dotenv_path: Path,
    edinet_api_key: None,  # Ensure API key is set  # noqa: ARG001
) -> None:
    """
    System test for 'kabu auth edinet' command.
    Requires EDINET_API_KEY to be set in environment.
    """
    # We don't provide input here, as the command should pick up from env vars
    # or prompt if not found. For system test, we assume env vars are set.
    result = runner.invoke(app, ["auth", "edinet"])

    assert result.exit_code == 0
    assert "EDINETのAPIキーを保存しました。" in result.stdout
    assert mock_dotenv_path.exists()
    assert "EDINET_API_KEY" in mock_dotenv_path.read_text()
