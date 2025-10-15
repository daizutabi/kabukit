from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio

from kabukit.jquants.client import JQuantsClient, _CalendarCacheManager

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture


@pytest_asyncio.fixture
async def client():
    async with JQuantsClient("test_token") as client:
        yield client


@pytest.fixture(autouse=True)
def reset_calendar_cache_manager(mocker: MockerFixture):
    # Patch the global _calendar_cache_manager to a new instance for each test
    # This ensures its lock is created in the context of the test's event loop
    mocker.patch(
        "kabukit.jquants.client._calendar_cache_manager",
        _CalendarCacheManager(),
    )


@pytest.fixture
def mock_jquants_client_context(mocker: MockerFixture) -> AsyncMock:
    """JQuantsClientの非同期コンテキストマネージャをモックするフィクスチャ"""
    mock_client_instance = mocker.AsyncMock()
    mocker.patch(
        "kabukit.jquants.concurrent.JQuantsClient",
        return_value=mocker.MagicMock(
            __aenter__=mocker.AsyncMock(return_value=mock_client_instance),
            __aexit__=mocker.AsyncMock(),
        ),
    )
    return mock_client_instance
