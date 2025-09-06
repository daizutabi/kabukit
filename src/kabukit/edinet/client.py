"""This module provides a client for the J-Quants API.

It handles authentication and provides methods to interact with
the API endpoints.
"""

from __future__ import annotations

import datetime
import os
from enum import StrEnum
from typing import TYPE_CHECKING

import polars as pl
from httpx import Client
from polars import DataFrame

from kabukit.config import load_dotenv

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any

    from httpx import HTTPStatusError  # noqa: F401
    from httpx._types import QueryParamTypes

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

    def get(self, url: str, params: dict[str, Any]) -> Any:
        if not self.api_key:
            msg = "API key is not available. Please set the API key first."
            raise KeyError(msg)

        params = params.copy()
        params["Subscription-Key"] = self.api_key

        resp = self.client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
