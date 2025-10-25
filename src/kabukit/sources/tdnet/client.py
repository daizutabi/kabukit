from __future__ import annotations

import re
from typing import TYPE_CHECKING

import httpx
import polars as pl
from bs4 import BeautifulSoup

from kabukit.sources.base import Client
from kabukit.utils.datetime import strpdate

from .document import iter_page_numbers, parse

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

    async def get(self, url: str) -> httpx.Response:
        """GETリクエストを送信する。

        Args:
            url: GETリクエストのURLパス。

        Returns:
            httpx.Response: APIからのレスポンスオブジェクト。

        Raises:
            httpx.HTTPStatusError: APIリクエストがHTTPエラーステータスを返した場合。
        """
        resp = await self.client.get(url)
        resp.raise_for_status()
        return resp

    async def get_dates(self) -> list[datetime.date]:
        """TDnetで利用可能な開示日一覧を取得する。

        Returns:
            list[date]: 利用可能な開示日のリスト。
        """
        resp = await self.get("I_main_00.html")

        soup = BeautifulSoup(resp.text, "lxml")
        daylist = soup.find("select", attrs={"name": "daylist"})

        if not daylist:
            return []

        pattern = re.compile(r"I_list_001_(\d{8})\.html")
        dates: list[datetime.date] = []

        for option in daylist.find_all("option"):
            value = option.get("value", "")
            if isinstance(value, str) and (m := pattern.search(value)):
                date = strpdate(m.group(1))
                dates.append(date)

        return dates

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

        url = f"I_list_{index:03}_{date}.html"
        resp = await self.get(url)
        return resp.text

    async def iter_pages(self, date: str | datetime.date) -> AsyncIterator[str]:
        """指定した日のTDnet開示情報一覧ページを非同期に反復処理する。

        Args:
            date (str | datetime.date): 取得する開示日の指定。

        Yields:
            str: 各ページのHTMLコンテンツ。
        """
        try:
            html = await self.get_page(date, index=1)
        except httpx.HTTPStatusError:
            return

        yield html

        for index in iter_page_numbers(html):
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

        items = [parse(page) async for page in self.iter_pages(date)]
        items = [item for item in items if not item.is_empty()]

        if not items:
            return pl.DataFrame()

        return pl.concat(items).select(
            pl.col("Code"),
            pl.lit(date).alias("DisclosedDate"),
            pl.exclude("Code"),
        )
