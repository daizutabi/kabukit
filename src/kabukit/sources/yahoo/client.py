from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from kabukit.sources.client import Client

from .parser import parse

if TYPE_CHECKING:
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

    async def get_quote(
        self,
        code: str,
        *,
        use_executor: bool = False,
    ) -> pl.DataFrame:
        """銘柄の株価、指標などの市場情報をYahooファイナンスから取得する。

        リアルタイムの株価、四本値、出来高に加え、PERやPBR、配当利回り
        といった主要な指標を含む包括的なデータを取得します。

        Args:
            code: 情報を取得する銘柄コード。
            use_executor: Trueの場合、別スレッドでパース処理を実行し、
                イベントループのブロッキングを防ぎます。デフォルトはFalse。

        Returns:
            polars.DataFrame: 銘柄の市場情報を含むDataFrame。
        """
        resp = await self.get(f"{code[:4]}.T")

        if len(code) == 4:
            code += "0"

        if use_executor:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, parse, resp.text, code)

        return parse(resp.text, code)
