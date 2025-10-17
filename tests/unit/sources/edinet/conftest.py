from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture


@pytest.fixture
def mock_edinet_client_context(mocker: MockerFixture) -> AsyncMock:
    """EdinetClientの非同期コンテキストマネージャをモックするフィクスチャ"""
    mock_client_instance = mocker.AsyncMock()
    mocker.patch(
        "kabukit.sources.edinet.concurrent.EdinetClient",
        return_value=mocker.MagicMock(
            __aenter__=mocker.AsyncMock(return_value=mock_client_instance),
            __aexit__=mocker.AsyncMock(),
        ),
    )
    return mock_client_instance
