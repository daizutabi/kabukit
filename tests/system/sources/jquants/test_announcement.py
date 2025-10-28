from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from kabukit.sources.jquants.client import JQuantsClient

pytestmark = pytest.mark.system


async def test_get(client: JQuantsClient) -> None:
    df = await client.get_announcement()
    assert df.width in [7, 0]
