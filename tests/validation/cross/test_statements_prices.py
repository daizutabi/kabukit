import pytest
from polars import DataFrame

from kabukit.core.statements import Statements
from kabukit.jquants.client import JQuantsClient
from tests.validation.conftest import pytestmark  # noqa: F401


@pytest.fixture(scope="module")
def number_of_shares(statements: Statements) -> DataFrame:
    return statements.number_of_shares()


@pytest.mark.asyncio
async def test_number_of_shares_6200(  # インソース
    number_of_shares: DataFrame,
    jquants_client: JQuantsClient,
) -> None:
    """発行済株式数の妥当性検証"""
    df = number_of_shares.filter(Code="62000")
    prices = await jquants_client.get_prices("6200")
    print(df)
    print(prices)
    assert 0
