from __future__ import annotations

from typing import TYPE_CHECKING

from kabukit.sources.base import Client

if TYPE_CHECKING:
    from httpx import Response

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

    async def get(self, url: str) -> Response:
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


# async def get_dates(self) -> list[date]:
#     """TDnetで利用可能な開示日一覧を取得する。

#     Returns:
#         list[date]: 利用可能な開示日のリスト。
#     """
#     resp = await self.get("I_main_00.html")
#     soup = BeautifulSoup(resp.text, "lxml")
#     daylist = soup.find("select", attrs={"name": "daylist"})
#     dates: list[date] = []
#     if daylist:
#         # daylist can be a Tag or a NavigableString
#         if hasattr(daylist, "find_all"):
#             for option in daylist.find_all("option"):
#                 if match := re.search(
#                     r"I_list_001_(\d{8})\.html",
#                     option.get("value", ""),
#                 ):
#                     dates.append(datetime.strptime(match.group(1), "%Y%m%d").date())
#     return dates
