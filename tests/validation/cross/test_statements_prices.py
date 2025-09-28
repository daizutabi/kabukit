import pytest
from polars import col as c

from kabukit.core.prices import Prices
from kabukit.core.statements import Statements
from tests.validation.conftest import pytestmark  # noqa: F401


@pytest.mark.asyncio
async def test_shares_consistency(statements: Statements) -> None:
    """
    最新のNumberOfSharesを基準に、過去の各時点での絶対株数を計算し、
    それが各決算短信のNumberOfSharesと一致するかを検証する。
    """
    from kabukit.jquants.concurrent import fetch

    # 過去に株式分割のあった銘柄コード
    codes = ["33500", "62000", "33990", "71870", "65420", "38160", "49230"]

    # 1. 必要なデータを準備
    stmt_df = statements.data.filter(c.Code.is_in(codes)).select(
        "Code",
        "Date",
        "NumberOfShares",
    )
    prices_df = Prices(await fetch("prices", codes)).with_relative_shares().data
