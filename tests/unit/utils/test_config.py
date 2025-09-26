from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def user_config_dir(mocker: MockerFixture, tmp_path: Path) -> MagicMock:
    def side_effect(name: str) -> str:
        return str(tmp_path / name)

    return mocker.patch(
        "kabukit.utils.config.user_config_dir",
        side_effect=side_effect,
    )


def test_get_dotenv_path(user_config_dir: MagicMock, tmp_path: Path) -> None:
    from kabukit.utils.config import get_dotenv_path

    path = get_dotenv_path()
    user_config_dir.assert_called_once_with("kabukit")
    assert path == tmp_path / "kabukit/.env"


def test_set_key() -> None:
    from kabukit.utils.config import get_dotenv_path, set_key

    set_key("KABUKIT_KEY1", "VALUE1")
    set_key("KABUKIT_KEY2", "VALUE2")
    text = "KABUKIT_KEY1='VALUE1'\nKABUKIT_KEY2='VALUE2'\n"
    assert get_dotenv_path().read_text() == text


def test_load_dotenv() -> None:
    from kabukit.utils.config import get_dotenv_path, load_dotenv

    path = get_dotenv_path()
    text = "KABUKIT_KEY1='VALUE1'\nKABUKIT_KEY2='VALUE2'\n"
    path.write_text(text)

    load_dotenv()
    assert os.environ["KABUKIT_KEY1"] == "VALUE1"
    assert os.environ["KABUKIT_KEY2"] == "VALUE2"
