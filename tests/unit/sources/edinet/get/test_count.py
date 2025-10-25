from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx import Response

from kabukit.sources.edinet.client import EdinetClient

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_count_success(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"metadata": {"status": "200", "resultset": {"count": 123}}}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    count = await client.get_count("2023-10-26")

    assert count == 123
    mock_get.assert_awaited_once_with(
        "/documents.json",
        params={"date": "2023-10-26", "type": 1},
    )


@pytest.mark.asyncio
async def test_get_count_fail(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"metadata": {"status": "404", "message": "error"}}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    count = await client.get_count("2023-10-26")

    assert count == 0
