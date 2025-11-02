from __future__ import annotations

from typing import TYPE_CHECKING

from kabukit.sources.client import Client

from .parser import iter_shares_links, iter_shares_urls

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

BASE_URL = "https://www.jpx.co.jp"
SHARES_URL = "/listing/co/01.html"


class JpxClient(Client):
    """JPXと非同期に対話するためのクライアント。

    `httpx.AsyncClient` をラップし、取得したHTMLのパース、
    `polars.DataFrame` への変換などを行う。

    Attributes:
        client (httpx.AsyncClient): APIリクエストを行うための非同期HTTPクライアント。
    """

    def __init__(self) -> None:
        super().__init__(BASE_URL)

    async def _iter_shares_urls(self) -> AsyncIterator[str]:
        response = await self.get(SHARES_URL)

        for url in iter_shares_urls(response.text):
            yield url

    async def _iter_shares_links(self) -> AsyncIterator[str]:
        async for url in self._iter_shares_urls():
            response = await self.get(url)
            for link in iter_shares_links(response.text):
                yield link
