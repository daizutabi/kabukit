from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import polars as pl
import pytest

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

MOCK_DF = pl.DataFrame({"A": [1, 2], "B": [3, 4]})
MOCK_CODE = "1234"
MOCK_PATH = "fake/path.csv"


@pytest.fixture
def mock_jquants_client(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.sources.jquants.client.JQuantsClient").return_value


@pytest.fixture
def mock_get_info(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jquants.concurrent.get_info",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


@pytest.fixture
def mock_get_statements(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jquants.concurrent.get_statements",
        new_callable=AsyncMock,
    )


@pytest.fixture
def mock_get_prices(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.jquants.concurrent.get_prices",
        new_callable=AsyncMock,
    )


@pytest.fixture
def mock_get_edinet_list(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.edinet.concurrent.get_list",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


@pytest.fixture
def mock_get_tdnet_list(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.tdnet.concurrent.get_list",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


@pytest.fixture
def mock_cache_write(mocker: MockerFixture) -> MagicMock:
    mock_cache_write = mocker.patch("kabukit.domain.cache.write")
    mock_cache_write.return_value = MOCK_PATH
    return mock_cache_write
