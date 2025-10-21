from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import polars as pl
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


def test_list_time(data: pl.DataFrame) -> None:
    x = data["時刻"]
    assert x.dtype == pl.Time
    assert x.is_not_null().all()


def test_list_code(data: pl.DataFrame) -> None:
    x = data["コード"]
    assert x.dtype == pl.String
    assert x.is_not_null().all()
    assert x.str.len_chars().min() == 5


def test_list_company_name(data: pl.DataFrame) -> None:
    x = data["会社名"]
    assert x.dtype == pl.String
    assert x.is_not_null().all()


def test_list_title(data: pl.DataFrame) -> None:
    x = data["表題"]
    assert x.dtype == pl.String
    assert x.is_not_null().all()


def test_list_pdf(data: pl.DataFrame) -> None:
    x = data["pdf"]
    assert x.dtype == pl.String
    assert x.is_not_null().all()
    assert x.str.ends_with(".pdf").all()


def test_list_xbrl(data: pl.DataFrame) -> None:
    x = data["xbrl"]
    assert x.dtype == pl.String
    assert x.drop_nulls().str.ends_with(".zip").all()


def test_list_market_name(data: pl.DataFrame) -> None:
    x = data["上場取引所"]
    assert x.dtype == pl.String
    assert x.is_not_null().all()


def test_list_history(data: pl.DataFrame) -> None:
    x = data["更新履歴"]
    assert x.dtype == pl.String
