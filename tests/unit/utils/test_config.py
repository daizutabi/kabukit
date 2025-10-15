from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture
if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import MagicMock

pytestmark = pytest.mark.unit


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


def test_save_config_key() -> None:
    from kabukit.utils.config import get_config_path, save_config_key

    save_config_key("KABUKIT_KEY1", "VALUE1")
    save_config_key("KABUKIT_KEY2", "VALUE2")
    text = 'KABUKIT_KEY1 = "VALUE1"\nKABUKIT_KEY2 = "VALUE2"\n'
    assert get_config_path().read_text() == text


def test_load_config() -> None:
    from kabukit.utils.config import get_config_path, load_config

    path = get_config_path()
    text = 'KABUKIT_KEY1 = "VALUE1"\nKABUKIT_KEY2 = "VALUE2"\n'
    path.write_text(text)

    config = load_config()
    assert config["KABUKIT_KEY1"] == "VALUE1"
    assert config["KABUKIT_KEY2"] == "VALUE2"
