"""This module provides a client for the J-Quants API.

It handles authentication and provides methods to interact with
the API endpoints.
"""

from __future__ import annotations

import os
from enum import StrEnum
from typing import TYPE_CHECKING

from httpx import Client
from polars import DataFrame

from kabukit.config import load_dotenv
from kabukit.params import get_params

if TYPE_CHECKING:
    import datetime
    from typing import Any

    from httpx import Response

API_VERSION = "v2"
BASE_URL = f"https://api.edinet-fsa.go.jp/api/{API_VERSION}"


class AuthKey(StrEnum):
    """Environment variable keys for EDINET authentication."""

    API_KEY = "EDINET_API_KEY"


class EdinetClient:
    client: Client
    api_key: str | None

    def __init__(self) -> None:
        self.client = Client(base_url=BASE_URL)
        load_dotenv()
        self.api_key = os.getenv(AuthKey.API_KEY)

    def get(self, url: str, params: dict[str, Any]) -> Response:
        if not self.api_key:
            msg = "API key is not available. Please set the API key first."
            raise KeyError(msg)

        params = params.copy()
        params["Subscription-Key"] = self.api_key

        resp = self.client.get(url, params=params)
        resp.raise_for_status()
        return resp

    def get_count(self, date: str | datetime.date) -> int:
        params = get_params(date=date, type=1)
        data = self.get("/documents.json", params).json()
        metadata = data["metadata"]

        if metadata["status"] != "200":
            return 0

        return metadata["resultset"]["count"]

    def get_list(self, date: str | datetime.date) -> DataFrame:
        params = get_params(date=date, type=2)
        data = self.get("/documents.json", params).json()

        if "results" not in data:
            return DataFrame()

        return DataFrame(data["results"], infer_schema_length=None)

    def get_document(self, doc_id: str, type: int) -> Any:
        params = get_params(type=type)
        data = self.get(f"/documents/{doc_id}", params)
