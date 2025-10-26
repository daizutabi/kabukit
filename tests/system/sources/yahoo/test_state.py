from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Any

pytestmark = pytest.mark.system


def test_state_keys(state: dict[str, Any]) -> None:
    pytest.fail(str(list(state.keys())))
