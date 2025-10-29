from __future__ import annotations

import polars as pl

from kabukit.sources.client import Client

from .parser import parse_quote

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

    async def get_quote(self, code: str) -> pl.DataFrame:
        """銘柄の株価、指標などの市場情報をYahooファイナンスから取得する。

        リアルタイムの株価、四本値、出来高に加え、PERやPBR、配当利回り
        といった主要な指標を含む包括的なデータを取得します。

        Args:
            code: 情報を取得する銘柄コード。

        Returns:
            polars.DataFrame: 銘柄の市場情報を含むDataFrame。
        """
        response = await self.get(f"{code[:4]}.T")

        df = parse_quote(response.text)

        if df.is_empty():
            return pl.DataFrame()

        if len(code) == 4:
            code += "0"

        return df.select(pl.lit(code).alias("Code"), pl.all())
