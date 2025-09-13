from __future__ import annotations

import io
import os
import zipfile
from enum import StrEnum
from typing import TYPE_CHECKING

import polars as pl
from httpx import AsyncClient
from polars import DataFrame

from kabukit.config import load_dotenv
from kabukit.params import get_params

if TYPE_CHECKING:
    import datetime

    from httpx import Response
    from httpx._types import QueryParamTypes

API_VERSION = "v2"
BASE_URL = f"https://api.edinet-fsa.go.jp/api/{API_VERSION}"


class AuthKey(StrEnum):
    """Environment variable keys for EDINET authentication."""

    API_KEY = "EDINET_API_KEY"


class EdinetClient:
    client: AsyncClient

    def __init__(self, api_key: str | None = None) -> None:
        self.client = AsyncClient(base_url=BASE_URL)
        self.set_api_key(api_key)

    def set_api_key(self, api_key: str | None = None) -> None:
        if api_key is None:
            load_dotenv()
            api_key = os.environ.get(AuthKey.API_KEY)

        if api_key:
            self.client.params = {"Subscription-Key": api_key}

    async def aclose(self) -> None:
        await self.client.aclose()

    async def get(self, url: str, params: QueryParamTypes) -> Response:
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

    async def get_document(self, doc_id: str, doc_type: int) -> Response:
        params = get_params(type=doc_type)
        return await self.get(f"/documents/{doc_id}", params)

    async def get_pdf(self, doc_id: str) -> bytes:
        resp = await self.get_document(doc_id, doc_type=2)
        if resp.headers["content-type"] == "application/pdf":
            return resp.content

        msg = "PDF is not available."
        raise ValueError(msg)

    async def get_zip(self, doc_id: str, doc_type: int) -> bytes:
        resp = await self.get_document(doc_id, doc_type=doc_type)
        if resp.headers["content-type"] == "application/octet-stream":
            return resp.content

        msg = "ZIP is not available."
        raise ValueError(msg)

    async def get_csv(self, doc_id: str) -> DataFrame:
        content = await self.get_zip(doc_id, doc_type=5)
        buffer = io.BytesIO(content)

        with zipfile.ZipFile(buffer) as zf:
            for info in zf.infolist():
                if info.filename.endswith(".csv"):
                    with zf.open(info) as f:
                        return pl.read_csv(
                            f.read(),
                            separator="\t",
                            encoding="utf-16-le",
                        )

        msg = "CSV is not available."
        raise ValueError(msg)
