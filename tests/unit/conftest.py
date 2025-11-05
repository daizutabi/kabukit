from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from unittest.mock import AsyncMock, MagicMock

    from pytest_mock import MockerFixture


@pytest.fixture
def mock_async_client(mocker: MockerFixture) -> MagicMock:
    mock_async_client = mocker.patch("kabukit.sources.client.AsyncClient").return_value
    mock_async_client.aclose = mocker.AsyncMock()
    return mock_async_client


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


@pytest.fixture
def mock_fetcher_get(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch("kabukit.utils.fetcher.get", new_callable=mocker.AsyncMock)
