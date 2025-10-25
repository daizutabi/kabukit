from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import pytest

if TYPE_CHECKING:
    from kabukit.sources.tdnet.client import TdnetClient

pytestmark = pytest.mark.system


def test_dates(dates: list[datetime.date]) -> None:
    today = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).date()
    assert today in dates
    assert len(dates) >= 28


@pytest.mark.asyncio
async def test_iter_pages(client: TdnetClient, date: datetime.date) -> None:
    index = 0

    async for html in client.iter_pages(date):
        index += 1
        date_str = date.strftime("%Y%m%d")
        url = f"I_list_{index:03}_{date_str}.html"

        assert url in html
