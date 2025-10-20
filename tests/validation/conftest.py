from __future__ import annotations

import pytest

from kabukit.domain.jquants.statements import Statements

try:
    _statements = Statements()
except FileNotFoundError:
    _statements = None


pytestmark = [
    pytest.mark.validation,
    pytest.mark.skipif(
        _statements is None,
        reason="No data found. Run `kabu get statements` first.",
    ),
]


@pytest.fixture(scope="module")
def statements() -> Statements:
    assert _statements is not None
    return _statements
