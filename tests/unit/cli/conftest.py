from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest
from polars import DataFrame

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

MOCK_DF = DataFrame({"A": [1, 2], "B": [3, 4]})
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
def mock_cache_write(mocker: MockerFixture) -> MagicMock:
    mock_cache_write = mocker.patch("kabukit.core.cache.write")
    mock_cache_write.return_value = MOCK_PATH
    return mock_cache_write


# @pytest.fixture
# def MockInfo(mocker: MockerFixture) -> MagicMock:
#     return mocker.patch("kabukit.core.info.Info")


# @pytest.fixture
# def mock_info(MockInfo: MagicMock) -> MagicMock:
#     instance = MockInfo.return_value
#     instance.write.return_value = MOCK_PATH
#     return instance


# @pytest.fixture
# def MockStatements(mocker: MockerFixture) -> MagicMock:
#     return mocker.patch("kabukit.core.statements.Statements")


# @pytest.fixture
# def mock_statements(MockStatements: MagicMock) -> MagicMock:
#     instance = MockStatements.return_value
#     instance.write.return_value = MOCK_PATH
#     return instance


# @pytest.fixture
# def MockPrices(mocker: MockerFixture) -> MagicMock:
#     return mocker.patch("kabukit.core.prices.Prices")


# @pytest.fixture
# def mock_prices(MockPrices: MagicMock) -> MagicMock:
#     instance = MockPrices.return_value
#     instance.write.return_value = MOCK_PATH
#     return instance


@pytest.fixture
def mock_get_entries(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.sources.edinet.concurrent.get_entries",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


# @pytest.fixture
# def MockEntries(mocker: MockerFixture) -> MagicMock:
#     return mocker.patch("kabukit.core.entries.Entries")


# @pytest.fixture
# def mock_entries(MockEntries: MagicMock) -> MagicMock:
#     instance = MockEntries.return_value
#     instance.write.return_value = MOCK_PATH
#     return instance
