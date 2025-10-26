from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio

from kabukit.sources.yahoo.client import YahooClient

if TYPE_CHECKING:
    from typing import Any

pytestmark = pytest.mark.system


@pytest_asyncio.fixture(scope="module")
async def text():
    async with YahooClient() as client:
        resp = await client.get("7203.T")
        yield resp.text


@pytest.fixture(scope="module")
def state(text: str):
    from kabukit.sources.yahoo.parser import get_preloaded_state

    return get_preloaded_state(text)


STATE_KEYS = [
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
    "incentive",
    "pageInfo",
    "customLogger",
    "subNewsHeadline",
    "subRecentAccess",
    "subStockRanking",
    "userInfo",
    "incentiveRankingList",
    "colorSetting",
    "feelingGraph",
    "stockAttentionRanking",
]


def test_state_len(state: dict[str, Any]) -> None:
    assert len(state) == len(STATE_KEYS)


@pytest.mark.parametrize("key", STATE_KEYS)
def test_state_keys(state: dict[str, Any], key: str) -> None:
    assert key in state


# def test_state_values(state: dict[str, Any]) -> None:
#     from kabukit.sources.yahoo.parser import iter_values

#     for k, v in iter_values(state):
#         print(k, v, v is None)

#     pytest.fail("debug")
