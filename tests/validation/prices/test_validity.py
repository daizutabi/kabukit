import pytest

from kabukit.core.prices import Prices
from kabukit.jquants.concurrent import fetch
from tests.validation.conftest import pytestmark  # noqa: F401


@pytest.mark.asyncio
async def test_relative_shares() -> None:
    codes = ["3350", "6200", "3399", "7187", "6542", "3816", "4923"]
    data = await fetch("prices", codes)
    df = Prices(data).with_relative_shares().data
    x = df["Close"]
    y = df["RawClose"] * df["RelativeShares"]
    assert (x - y).abs().le(0.1).all()  # 誤差0.1円以内
