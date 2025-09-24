from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from kabukit.utils import config


@patch("kabukit.utils.config.dotenv")
@patch("kabukit.utils.config.get_dotenv_path")
def test_set_key(
    mock_get_dotenv_path: MagicMock,
    mock_dotenv: MagicMock,
):
    # Arrange
    test_path = Path("/tmp/.env")  # noqa: S108
    mock_get_dotenv_path.return_value = test_path
    mock_dotenv.set_key.return_value = (True, "TEST_KEY", "TEST_VALUE")

    # Act
    key = "TEST_KEY"
    value = "TEST_VALUE"
    config.set_key(key, value)

    # Assert
    mock_get_dotenv_path.assert_called_once()
    mock_dotenv.set_key.assert_called_once_with(test_path, key, value)
