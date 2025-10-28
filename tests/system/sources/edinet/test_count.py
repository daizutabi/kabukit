from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from kabukit.sources.edinet.client import EdinetClient

pytestmark = pytest.mark.system


async def test_count(client: EdinetClient) -> None:
    assert await client.get_count("2025-09-04") == 211


async def test_count_zero(client: EdinetClient) -> None:
    assert await client.get_count("1000-01-01") == 0


async def test_count_status_not_200(client: EdinetClient) -> None:
    assert await client.get_count("") == 0
