from __future__ import annotations

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
