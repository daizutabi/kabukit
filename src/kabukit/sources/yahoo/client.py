from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from kabukit.sources.base import Client

from .state import parse

if TYPE_CHECKING:
    import httpx
    import polars as pl


BASE_URL = "https://finance.yahoo.co.jp/quote"


class YahooClient(Client):
    """Yahooファイナンスと非同期に対話するためのクライアント。

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

    async def get_state(self, code: str) -> pl.DataFrame:
        """Yahooファイナンスの情報を取得する。

        Args:
            code: 取得する銘柄コード。

        Returns:
            polars.DataFrame: 取得した情報を含むDataFrame。
        """
        resp = await self.get(f"{code[:4]}.T")
        # return parse(resp.text, code)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, parse, resp.text, code)
