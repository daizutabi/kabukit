from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio

from kabukit.jquants.client import JQuantsClient

if TYPE_CHECKING:
    from unittest.mock import AsyncMock, MagicMock

    from pytest_mock import MockerFixture


@pytest_asyncio.fixture
async def client():
    async with JQuantsClient("test_token") as client:
        yield client


@pytest.fixture(autouse=True)
def reset_calendar_cache():
    from kabukit.jquants.client import _calendar_cache_manager

    _calendar_cache_manager._holidays = None  # noqa: SLF001


@pytest.fixture
def mock_async_client(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.core.client.AsyncClient").return_value


@pytest.fixture
def mock_post(mock_async_client: MagicMock, mocker: MockerFixture) -> AsyncMock:
    mock_post = mocker.AsyncMock()
    mock_async_client.post = mock_post
    return mock_post


@pytest.fixture
def mock_get(mock_async_client: MagicMock, mocker: MockerFixture) -> AsyncMock:
    mock_get = mocker.AsyncMock()
    mock_async_client.get = mock_get
    return mock_get
