from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import tenacity
from httpx import AsyncClient

if TYPE_CHECKING:
    from typing import Self

    from httpx import Response
    from httpx._types import QueryParamTypes


def is_retryable(e: BaseException) -> bool:
    """例外がリトライ可能なネットワークエラーであるかを判定する。"""
    return isinstance(e, (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError))


class Client:
    client: AsyncClient

    def __init__(self, base_url: str = "") -> None:
        self.client = AsyncClient(base_url=base_url, timeout=20)

    async def aclose(self) -> None:
        """HTTPクライアントを閉じる。"""
        await self.client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # pyright: ignore[reportMissingParameterType, reportUnknownParameterType]  # noqa: ANN001
        await self.aclose()

    @tenacity.retry(
        reraise=True,
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
        retry=tenacity.retry_if_exception(is_retryable),
    )
    async def get(self, url: str, params: QueryParamTypes | None = None) -> Response:
        """リトライ処理を伴うGETリクエストを送信する。

        ネットワークエラーが発生した場合、指数関数的バックオフを用いて
        最大3回までリトライする。

        Args:
            url: GETリクエストのURLパス。
            params: リクエストのクエリパラメータ。

        Returns:
            httpx.Response: APIからのレスポンスオブジェクト。

        Raises:
            httpx.HTTPStatusError: APIリクエストがHTTPエラーステータスを返した場合。
        """
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response
