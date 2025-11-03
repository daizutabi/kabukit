from __future__ import annotations

from typing import TYPE_CHECKING

from kabukit.sources.client import Client

from .parser import iter_shares_html_urls, iter_shares_pdf_urls, parse_shares

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    import polars as pl

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

    async def iter_shares_html_urls(self) -> AsyncIterator[str]:
        response = await self.get(SHARES_URL)

        for html_url in iter_shares_html_urls(response.text):
            yield html_url

    async def _iter_shares_pdf_urls(self, html_url: str) -> AsyncIterator[str]:
        response = await self.get(html_url)

        for pdf_url in iter_shares_pdf_urls(response.text):
            yield pdf_url

    async def iter_shares_pdf_urls(
        self,
        html_url: str | None = None,
    ) -> AsyncIterator[str]:
        if html_url:
            async for pdf_url in self._iter_shares_pdf_urls(html_url):
                yield pdf_url

        else:
            async for url in self.iter_shares_html_urls():
                async for pdf_url in self._iter_shares_pdf_urls(url):
                    yield pdf_url

    async def get_shares(self, pdf_url: str) -> pl.DataFrame:
        response = await self.get(pdf_url)
        return parse_shares(response.content)
