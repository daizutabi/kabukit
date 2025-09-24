from __future__ import annotations

from functools import cache
from pathlib import Path

import dotenv
from platformdirs import user_config_dir


@cache
def get_dotenv_path() -> Path:
    """Return the path to the .env file in the user config directory."""
    config_dir = Path(user_config_dir("kabukit"))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / ".env"


@cache
def load_dotenv() -> bool:
    dotenv_path = get_dotenv_path()
    return dotenv.load_dotenv(dotenv_path)


def set_key(key: str, value: str) -> tuple[bool | None, str, str]:
    dotenv_path = get_dotenv_path()
    return dotenv.set_key(dotenv_path, key, value)
