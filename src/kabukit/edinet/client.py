from __future__ import annotations

import io
import os
import zipfile
from enum import StrEnum
from typing import TYPE_CHECKING

import httpx
from polars import DataFrame
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from kabukit.core.client import Client
from kabukit.utils.config import load_dotenv
from kabukit.utils.params import get_params

from .doc import clean_csv, clean_entries, clean_pdf, read_csv

if TYPE_CHECKING:
    import datetime

    from httpx import Response
    from httpx._types import QueryParamTypes

API_VERSION = "v2"
BASE_URL = f"https://api.edinet-fsa.go.jp/api/{API_VERSION}"


def is_retryable(e: BaseException) -> bool:
    """Return True if the exception is a retryable network error."""
    return isinstance(e, (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError))


class AuthKey(StrEnum):
    """Environment variable keys for EDINET authentication."""

    API_KEY = "EDINET_API_KEY"


class EdinetClient(Client):
    def __init__(self, api_key: str | None = None) -> None:
        super().__init__(BASE_URL)
        self.set_api_key(api_key)

    def set_api_key(self, api_key: str | None = None) -> None:
        if api_key is None:
            load_dotenv()
            api_key = os.environ.get(AuthKey.API_KEY)

        if api_key:
            self.client.params = {"Subscription-Key": api_key}

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception(is_retryable),
    )
    async def get(self, url: str, params: QueryParamTypes) -> Response:
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        return resp

    async def get_count(self, date: str | datetime.date) -> int:
        """書類一覧 API を使い、特定の日付の提出書類数を取得する。

        Args:
            date (str | datetime.date): 取得対象の日付 (YYYY-MM-DD)

        Returns:
            int: 書類数

        """
        params = get_params(date=date, type=1)
        resp = await self.get("/documents.json", params)
        data = resp.json()
        metadata = data["metadata"]

        if metadata["status"] != "200":
            return 0

        return metadata["resultset"]["count"]

    async def get_entries(self, date: str | datetime.date) -> DataFrame:
        """書類一覧 API を使い、特定の日付の提出書類一覧を取得する。

        Args:
            date (str | datetime.date): 取得対象の日付 (YYYY-MM-DD)

        Returns:
            DataFrame: 提出書類一覧を格納した DataFrame
        """
        params = get_params(date=date, type=2)
        resp = await self.get("/documents.json", params)
        data = resp.json()

        if "results" not in data:
            return DataFrame()

        df = DataFrame(data["results"], infer_schema_length=None)

        if df.is_empty():
            return df

        return clean_entries(df, date)

    async def get_response(self, doc_id: str, doc_type: int) -> Response:
        params = get_params(type=doc_type)
        return await self.get(f"/documents/{doc_id}", params)

    async def get_pdf(self, doc_id: str) -> DataFrame:
        resp = await self.get_response(doc_id, doc_type=2)
        if resp.headers["content-type"] == "application/pdf":
            return clean_pdf(resp.content, doc_id)

        msg = "PDF is not available."
        raise ValueError(msg)

    async def get_zip(self, doc_id: str, doc_type: int) -> bytes:
        resp = await self.get_response(doc_id, doc_type=doc_type)
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
                        df = read_csv(f.read())
                        return clean_csv(df, doc_id)

        msg = "CSV is not available."
        raise ValueError(msg)

    async def get_document(self, doc_id: str, *, pdf: bool = False) -> DataFrame:
        if pdf:
            return await self.get_pdf(doc_id)

        return await self.get_csv(doc_id)
