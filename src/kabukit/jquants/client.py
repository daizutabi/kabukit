"""This module provides a client for the J-Quants API.

It handles authentication and provides methods to interact with
the API endpoints.
"""

from __future__ import annotations

import datetime
import os
from enum import StrEnum
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl
from dotenv import load_dotenv, set_key
from httpx import Client
from platformdirs import user_config_dir
from polars import DataFrame

if TYPE_CHECKING:
    from typing import Any

    from httpx import HTTPStatusError  # noqa: F401
    from httpx._types import QueryParamTypes

API_VERSION = "v1"


class AuthKey(StrEnum):
    """Environment variable keys for J-Quants authentication."""

    REFRESH_TOKEN = "JQUANTS_REFRESH_TOKEN"  # noqa: S105
    ID_TOKEN = "JQUANTS_ID_TOKEN"  # noqa: S105


class JQuantsClient:
    """A client for interacting with the J-Quants API.

    This client manages API authentication tokens (refresh and ID)
    and provides methods to access various J-Quants API
    endpoints. Tokens are loaded from and saved to a file in the
    user's standard config directory.

    Attributes:
        client: An httpx.Client instance for making API requests.
        refresh_token: The refresh token for authentication.
        id_token: The ID token for API requests.
    """

    client: Client
    refresh_token: str
    id_token: str

    def __init__(self) -> None:
        """Initializes the JQuantsClient.

        It sets up the httpx client, determines the config path,
        loads authentication tokens, and sets the auth header if an
        ID token is present.
        """
        self.client = Client(base_url=f"https://api.jquants.com/{API_VERSION}")
        self.load_tokens()

    @cached_property
    def dotenv_path(self) -> Path:
        config_dir = Path(user_config_dir("kabukit"))
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / ".env"

    def load_tokens(self) -> None:
        """Loads tokens from the .env file."""
        load_dotenv(self.dotenv_path)
        self.refresh_token = os.environ.get(AuthKey.REFRESH_TOKEN) or ""
        self.id_token = os.environ.get(AuthKey.ID_TOKEN) or ""

    def auth(self, mailaddress: str, password: str) -> None:
        """Authenticates, saves tokens, and sets the auth header.

        Args:
            mailaddress: The user's email address.
            password: The user's password.

        Raises:
            HTTPStatusError: If any API request fails.
        """
        self.refresh_token = self.get_refresh_token(mailaddress, password)
        self.id_token = self.get_id_token(self.refresh_token)
        set_key(self.dotenv_path, AuthKey.REFRESH_TOKEN, self.refresh_token)
        set_key(self.dotenv_path, AuthKey.ID_TOKEN, self.id_token)

    def post(self, url: str, json: Any | None = None) -> Any:
        resp = self.client.post(url, json=json)
        resp.raise_for_status()
        return resp.json()

    def get_refresh_token(self, mailaddress: str, password: str) -> str:
        """Gets a new refresh token from the API.

        Args:
            mailaddress: The user's email address.
            password: The user's password.

        Returns:
            The new refresh token.

        Raises:
            httpx.HTTPStatusError: If the API request fails.
        """
        json = {"mailaddress": mailaddress, "password": password}
        return self.post("/token/auth_user", json=json)["refreshToken"]

    def get_id_token(self, refresh_token: str) -> str:
        """Gets a new ID token from the API.

        Args:
            refresh_token: The refresh token to use.

        Returns:
            The new ID token.

        Raises:
            HTTPStatusError: If the API request fails.
        """
        url = f"/token/auth_refresh?refreshtoken={refresh_token}"
        return self.post(url)["idToken"]

    def get(self, url: str, params: QueryParamTypes | None = None) -> Any:
        headers = {"Authorization": f"Bearer {self.id_token}"}
        resp = self.client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def get_listed_info(
        self,
        code: str | None = None,
        date: str | datetime.date | None = None,
    ) -> DataFrame:
        params: dict[str, str] = {}
        if code:
            params["code"] = code
        if date:
            if isinstance(date, datetime.date):
                date = date.strftime("%Y-%m-%d")
            params["date"] = date

        data = self.get("/listed/info", params)["info"]
        return DataFrame(data).with_columns(pl.col("Date").str.to_date())
