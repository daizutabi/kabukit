from unittest.mock import AsyncMock, MagicMock

import pytest
from polars import DataFrame
from pytest_mock import MockerFixture

MOCK_DF = DataFrame({"A": [1, 2], "B": [3, 4]})
MOCK_CODE = "1234"
MOCK_PATH = "fake/path.csv"


@pytest.fixture
def jquants_client(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.jquants.client.JQuantsClient").return_value


@pytest.fixture
def get_info(jquants_client: MagicMock) -> AsyncMock:
    get_info = AsyncMock(return_value=MOCK_DF)
    jquants_client.__aenter__.return_value.get_info = get_info
    return get_info


@pytest.fixture
def get_statements(jquants_client: MagicMock) -> AsyncMock:
    get_statements = AsyncMock(return_value=MOCK_DF)
    jquants_client.__aenter__.return_value.get_statements = get_statements
    return get_statements


@pytest.fixture
def get_prices(jquants_client: MagicMock) -> AsyncMock:
    get_prices = AsyncMock(return_value=MOCK_DF)
    jquants_client.__aenter__.return_value.get_prices = get_prices
    return get_prices


@pytest.fixture
def fetch_all(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        "kabukit.jquants.concurrent.fetch_all",
        new_callable=AsyncMock,
        return_value=MOCK_DF,
    )


@pytest.fixture
def Info(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.core.info.Info")


@pytest.fixture
def info(Info: MagicMock) -> MagicMock:  # noqa: N803
    info = Info.return_value
    info.write.return_value = MOCK_PATH
    return info


@pytest.fixture
def Statements(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.core.statements.Statements")


@pytest.fixture
def statements(Statements: MagicMock) -> MagicMock:  # noqa: N803
    instance = Statements.return_value
    instance.write.return_value = MOCK_PATH
    return instance


@pytest.fixture
def Prices(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.core.prices.Prices")


@pytest.fixture
def prices(Prices: MagicMock) -> MagicMock:  # noqa: N803
    instance = Prices.return_value
    instance.write.return_value = MOCK_PATH
    return instance
