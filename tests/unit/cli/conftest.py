from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from polars import DataFrame

if TYPE_CHECKING:
    from unittest.mock import AsyncMock, MagicMock

    from pytest_mock import MockerFixture

MOCK_DF = DataFrame({"A": [1, 2], "B": [3, 4]})
MOCK_CODE = "1234"
MOCK_PATH = "fake/path.csv"


@pytest.fixture
def mock_jquants_client(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.jquants.client.JQuantsClient").return_value


@pytest.fixture
def mock_get_info(mock_jquants_client: MagicMock, mocker: MockerFixture) -> AsyncMock:
    mock_get_info = mocker.AsyncMock(return_value=MOCK_DF)
    mock_jquants_client.__aenter__.return_value.get_info = mock_get_info
    return mock_get_info


@pytest.fixture
def mock_get_statements(
    mock_jquants_client: MagicMock,
    mocker: MockerFixture,
) -> AsyncMock:
    mock_get_statements = mocker.AsyncMock(return_value=MOCK_DF)
    mock_jquants_client.__aenter__.return_value.get_statements = mock_get_statements
    return mock_get_statements


@pytest.fixture
def mock_get_prices(mock_jquants_client: MagicMock, mocker: MockerFixture) -> AsyncMock:
    mock_get_prices = mocker.AsyncMock(return_value=MOCK_DF)
    mock_jquants_client.__aenter__.return_value.get_prices = mock_get_prices
    return mock_get_prices


@pytest.fixture
def mock_get_all(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.jquants.concurrent.get_all",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


@pytest.fixture
def MockInfo(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.core.info.Info")


@pytest.fixture
def mock_info(MockInfo: MagicMock) -> MagicMock:  # noqa: N803
    instance = MockInfo.return_value
    instance.write.return_value = MOCK_PATH
    return instance


@pytest.fixture
def MockStatements(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.core.statements.Statements")


@pytest.fixture
def mock_statements(MockStatements: MagicMock) -> MagicMock:  # noqa: N803
    instance = MockStatements.return_value
    instance.write.return_value = MOCK_PATH
    return instance


@pytest.fixture
def MockPrices(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.core.prices.Prices")


@pytest.fixture
def mock_prices(MockPrices: MagicMock) -> MagicMock:  # noqa: N803
    instance = MockPrices.return_value
    instance.write.return_value = MOCK_PATH
    return instance


@pytest.fixture
def mock_fetch_documents(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.edinet.concurrent.fetch_documents",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


@pytest.fixture
def mock_fetch_csv(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.edinet.concurrent.fetch_csv",
        new_callable=mocker.AsyncMock,
        return_value=MOCK_DF,
    )


@pytest.fixture
def MockDocuments(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.core.documents.Documents")


@pytest.fixture
def mock_documents(MockDocuments: MagicMock) -> MagicMock:  # noqa: N803
    instance = MockDocuments.return_value
    instance.write.return_value = MOCK_PATH
    return instance
