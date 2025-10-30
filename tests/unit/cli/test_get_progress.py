from __future__ import annotations

import pytest

from kabukit.cli.get import CustomTqdm

pytestmark = pytest.mark.unit


def test_custom_tqdm() -> None:
    tqdm = CustomTqdm(total=10)
    assert tqdm.ncols == 80
    tqdm.close()
