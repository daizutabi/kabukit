from __future__ import annotations

import pytest

from kabukit.domain.edinet.list import List

pytestmark = pytest.mark.unit


def test_data_dir() -> None:
    path = List.data_dir()
    assert path.parts[-3:] == ("kabukit", "edinet", "list")
