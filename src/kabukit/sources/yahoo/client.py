from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, Tag

from kabukit.sources.base import Client

if TYPE_CHECKING:
    from typing import Any

    import httpx


BASE_URL = "https://finance.yahoo.co.jp/quote"

PRELOADED_STATE_PATTERN = re.compile(r"window\.__PRELOADED_STATE__\s*=\s*(\{.*\})")


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

    async def get_state_dict(self, code: str) -> dict[str, Any]:
        resp = await self.get(f"{code[:4]}.T")

        soup = BeautifulSoup(resp.text, "lxml")
        script = soup.find("script", string=PRELOADED_STATE_PATTERN)  # pyright: ignore[reportCallIssue, reportArgumentType, reportUnknownVariableType], # ty: ignore[no-matching-overload]

        if not isinstance(script, Tag):
            msg = "Could not find the __PRELOADED_STATE__ script tag."
            raise TypeError(msg)

        match = PRELOADED_STATE_PATTERN.search(script.text)

        if match is None:
            msg = "Could not find __PRELOADED_STATE__ JSON data."
            raise ValueError(msg)

        return json.loads(match.group(1))
