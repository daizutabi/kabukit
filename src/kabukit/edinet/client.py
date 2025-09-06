from __future__ import annotations

import io
import os
import zipfile
from enum import StrEnum
from typing import TYPE_CHECKING

from httpx import AsyncClient
from polars import DataFrame

from kabukit.config import load_dotenv
from kabukit.params import get_params

if TYPE_CHECKING:
    import datetime
    from typing import Any, Self

    from httpx import Response

API_VERSION = "v2"
BASE_URL = f"https://api.edinet-fsa.go.jp/api/{API_VERSION}"


class AuthKey(StrEnum):
    """Environment variable keys for EDINET authentication."""

    API_KEY = "EDINET_API_KEY"


class EdinetClient:
    client: AsyncClient
    api_key: str | None

    def __init__(self, client: AsyncClient) -> None:
        self.client = client
        load_dotenv()
        self.api_key = os.getenv(AuthKey.API_KEY)

    @classmethod
    def create(cls) -> Self:
        client = AsyncClient(base_url=BASE_URL)

        return cls(client)

    async def aclose(self) -> None:
        await self.client.aclose()

    async def get(self, url: str, params: dict[str, Any]) -> Response:
        if not self.api_key:
            msg = "API key is not available. Please set the API key first."
            raise KeyError(msg)

        params = params.copy()
        params["Subscription-Key"] = self.api_key

        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        return resp

    async def get_count(self, date: str | datetime.date) -> int:
        params = get_params(date=date, type=1)
        resp = await self.get("/documents.json", params)
        data = resp.json()
        metadata = data["metadata"]

        if metadata["status"] != "200":
            return 0

        return metadata["resultset"]["count"]

    async def get_list(self, date: str | datetime.date) -> DataFrame:
        params = get_params(date=date, type=2)
        resp = await self.get("/documents.json", params)
        data = resp.json()

        if "results" not in data:
            return DataFrame()

        return DataFrame(data["results"], infer_schema_length=None)

    async def get_document(self, doc_id: str, type: int) -> Response:
        params = get_params(type=type)
        return await self.get(f"/documents/{doc_id}", params)

    async def get_pdf(self, doc_id: str) -> bytes:
        resp = await self.get_document(doc_id, type=2)
        if resp.headers["content-type"] != "application/pdf":
            msg = "PDF is not available."
            raise ValueError(msg)

        return resp.content

    async def get_zip(self, doc_id: str, type: int) -> zipfile.ZipFile:
        resp = await self.get_document(doc_id, type=type)
        if resp.headers["content-type"] != "application/octet-stream":
            msg = "ZIP is not available."
            raise ValueError(msg)

        buffer = io.BytesIO(resp.content)
        return zipfile.ZipFile(buffer)
