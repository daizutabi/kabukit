from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import polars as pl

from kabukit.sources.client import Client
from kabukit.sources.datetime import with_date
from kabukit.utils.datetime import strpdate

from .parser import iter_dates, iter_page_numbers, parse_list
from .transform import transform_list

if TYPE_CHECKING:
    import datetime
    from collections.abc import AsyncIterator


BASE_URL = "https://www.release.tdnet.info/inbs"


class TdnetClient(Client):
    """TDnetと非同期に対話するためのクライアント。

    `httpx.AsyncClient` をラップし、取得したHTMLのパース、
    `polars.DataFrame` への変換などを行う。

    Attributes:
        client (httpx.AsyncClient): APIリクエストを行うための非同期HTTPクライアント。
    """

    def __init__(self) -> None:
        super().__init__(BASE_URL)

    async def get_dates(self) -> list[datetime.date]:
        """TDnetで利用可能な開示日一覧を取得する。

        Returns:
            list[date]: 利用可能な開示日のリスト。
        """
        response = await self.get("I_main_00.html")
        return list(iter_dates(response.text))

    async def get_page(self, date: str | datetime.date, index: int) -> str:
        """指定した日のTDnet開示情報一覧ページを取得する。

        Args:
            date (str | datetime.date): 取得する開示日の指定。
            index (int): 取得するページのインデックス（1から始まる）。

        Returns:
            str: ページのHTMLコンテンツ。
        """
        if not isinstance(date, str):
            date = date.strftime("%Y%m%d")

        response = await self.get(f"I_list_{index:03}_{date}.html")
        return response.text

    async def iter_pages(self, date: str | datetime.date) -> AsyncIterator[str]:
        """指定した日のTDnet開示情報一覧ページを非同期に反復処理する。

        Args:
            date (str | datetime.date): 取得する開示日の指定。

        Yields:
            str: 各ページのHTMLコンテンツ。
        """
        try:
            text = await self.get_page(date, index=1)
        except httpx.HTTPStatusError:
            return

        yield text

        for index in iter_page_numbers(text):
            if index != 1:
                yield await self.get_page(date, index)

    async def get_list(self, date: str | datetime.date) -> pl.DataFrame:
        """指定した日付の開示書類一覧を取得する。

        Args:
            date (str | datetime.date): 取得する開示日。

        Returns:
            pl.DataFrame: 開示書類一覧を含むDataFrame。
        """
        if isinstance(date, str):
            date = strpdate(date)

        items = [parse_list(page) async for page in self.iter_pages(date)]
        items = [item for item in items if not item.is_empty()]

        if not items:
            return pl.DataFrame()

        df = pl.concat(items)
        df = transform_list(df, date)
        return await with_date(df)
