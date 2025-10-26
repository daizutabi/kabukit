from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio

from kabukit.sources.yahoo.client import YahooClient

if TYPE_CHECKING:
    from typing import Any

pytestmark = pytest.mark.system


@pytest_asyncio.fixture(scope="module")
async def state():
    async with YahooClient() as client:
        yield await client.get_state_dict("72030")


@pytest.mark.parametrize(
    "key",
    [
        "commonPortfolioAddition",
        "commonPr",
        "headerApology",
        "headerPortfolio",
        "mainStocksDetail",
        "mainStocksPriceBoard",
        "mainIndicatorDetail",
        "mainItemDetailChartSetting",
        "mainRelatedItem",
        "mainYJChart",
        "mainYJCompareChart",
        "mainStocksHistory",
        "mainStocksMarginHistory",
        "mainStocksHistoryPage",
        "mainStocksNews",
        "mainStocksDisclosure",
        "mainStocksForecast",
        "mainStocksProfile",
        "mainStocksPost",
        "mainStocksDividend",
        "mainStocksPressReleaseSchedule",
        "mainStocksPressReleaseSummary",
        "stockPredictions",
        "stockPerformance",
    ],
)
def test_state_keys(state: dict[str, Any], key: str) -> None:
    assert key in state


def test_state_values(state: dict[str, Any]) -> None:
    from kabukit.sources.yahoo.state import iter_values

    assert list(iter_values(state))

    # for k, v in iter_values(state):
    #     print(k, v)
    # assert 0
