import pytest
from polars import DataFrame
from polars import col as c

from kabukit.core.prices import Prices
from kabukit.core.statements import Statements
from tests.validation.conftest import pytestmark  # noqa: F401


@pytest.mark.asyncio
async def test_number_of_shares(statements: Statements) -> None:
    """発行済株式数の妥当性検証"""
    from kabukit.jquants.concurrent import fetch

    codes = ["33500", "62000", "33990", "71870", "65420", "38160", "49230"]
    number_of_shares = statements.number_of_shares().filter(c.Code.is_in(codes))
    prices = Prices(await fetch("prices", codes)).with_relative_shares().data
