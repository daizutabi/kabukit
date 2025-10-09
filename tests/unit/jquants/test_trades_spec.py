from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest
from httpx import Response

from kabukit.jquants.client import JQuantsClient

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture


@pytest.mark.asyncio
async def test_get(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"trades_spec": [{"Date": "2025-01-01"}]}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_trades_spec()
    assert df["Date"].to_list() == [datetime.date(2025, 1, 1)]


@pytest.mark.asyncio
async def test_empty(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json: dict[str, list[dict[str, str]]] = {"trades_spec": []}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_trades_spec()
    assert df.is_empty()
