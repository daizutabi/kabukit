from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def user_cache_dir(mocker: MockerFixture, tmp_path: Path) -> MagicMock:
    def side_effect(name: str) -> str:
        return str(tmp_path / name)

    return mocker.patch("kabukit.utils.config.user_cache_dir", side_effect=side_effect)


def test_get_cache_dir(user_cache_dir: MagicMock, tmp_path: Path) -> None:
    from kabukit.utils.config import get_cache_dir

    path = get_cache_dir()
    user_cache_dir.assert_called_once_with("kabukit")
    assert path == tmp_path / "kabukit"


@pytest.fixture(autouse=True)
def user_config_dir(mocker: MockerFixture, tmp_path: Path) -> MagicMock:
    def side_effect(name: str) -> str:
        return str(tmp_path / name)

    return mocker.patch("kabukit.utils.config.user_config_dir", side_effect=side_effect)


def test_get_config_path(user_config_dir: MagicMock, tmp_path: Path) -> None:
    from kabukit.utils.config import get_config_path

    path = get_config_path()
    user_config_dir.assert_called_once_with("kabukit")
    assert path == tmp_path / "kabukit/config.toml"


def test_load_config_empty_file_if_not_exists() -> None:
    from kabukit.utils.config import get_config_path, load_config

    # Ensure config file does not exist
    path = get_config_path()
    if path.exists():
        path.unlink()

    config = load_config()
    assert config == {}


def test_load_config_existing_file() -> None:
    from kabukit.utils.config import get_config_path, load_config

    path = get_config_path()
    text = 'KABUKIT_KEY1 = "VALUE1"\nKABUKIT_KEY2 = "VALUE2"\n'
    path.write_text(text)

    config = load_config()
    assert config == {"KABUKIT_KEY1": "VALUE1", "KABUKIT_KEY2": "VALUE2"}


def test_save_config_key_add() -> None:
    from kabukit.utils.config import load_config, save_config_key

    save_config_key("KABUKIT_KEY1", "VALUE1")
    save_config_key("KABUKIT_KEY2", "VALUE2")
    loaded_config = load_config()

    assert loaded_config == {"KABUKIT_KEY1": "VALUE1", "KABUKIT_KEY2": "VALUE2"}


def test_save_config_key_update() -> None:
    from kabukit.utils.config import load_config, save_config_key

    save_config_key("KABUKIT_KEY1", "NEW_VALUE1")
    save_config_key("KABUKIT_KEY1", "NEW_VALUE2")
    loaded_config = load_config()

    assert loaded_config == {"KABUKIT_KEY1": "NEW_VALUE2"}


def test_get_config_value_from_config() -> None:
    from kabukit.utils.config import get_config_value, save_config_key

    save_config_key("KABUKIT_KEY1", "VALUE1")
    save_config_key("KABUKIT_KEY2", "VALUE2")
    assert get_config_value("KABUKIT_KEY1") == "VALUE1"
    assert get_config_value("KABUKIT_KEY2") == "VALUE2"


def test_get_config_value_fallback_to_env(mocker: MockerFixture) -> None:
    from kabukit.utils.config import get_config_value

    mocker.patch.dict(os.environ, {"ENV_KEY": "ENV_VALUE"})
    assert get_config_value("ENV_KEY") == "ENV_VALUE"
    assert get_config_value("NON_EXISTENT_KEY") is None


def test_get_config_value_precedence(mocker: MockerFixture) -> None:
    from kabukit.utils.config import get_config_value, save_config_key

    save_config_key("PRECEDENCE_KEY", "CONFIG_VALUE")
    mocker.patch.dict(os.environ, {"PRECEDENCE_KEY": "ENV_VALUE"})
    assert get_config_value("PRECEDENCE_KEY") == "CONFIG_VALUE"
