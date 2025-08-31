"""This module provides a client for the J-Quants API.

It handles authentication and provides methods to interact with
the API endpoints.
"""

from __future__ import annotations

import os
from enum import StrEnum

from dotenv import find_dotenv, load_dotenv, set_key
from httpx import Client

API_VERSION = "v1"


class Key(StrEnum):
    """Environment variable keys for J-Quants authentication."""

    REFRESH_TOKEN = "JQUANTS_REFRESH_TOKEN"  # noqa: S105
    ID_TOKEN = "JQUANTS_ID_TOKEN"  # noqa: S105


class JQuantsClient:
    """A client for interacting with the J-Quants API.

    This client manages API authentication tokens (refresh and ID)
    and provides methods to access various J-Quants API
    endpoints. Tokens are loaded from environment variables and
    automatically saved to a .env file when they are issued.

    Attributes:
        client: An httpx.Client instance for making API requests.
        refresh_token: The refresh token for authentication.
        id_token: The ID token for API requests.
    """

    client: Client
    refresh_token: str | None
    id_token: str | None

    def __init__(self) -> None:
        """Initializes the JQuantsClient.

        It sets up the httpx client and loads authentication
        tokens from environment variables.
        """
        self.client = Client(base_url=f"https://api.jquants.com/{API_VERSION}")
        load_dotenv()
        self.refresh_token = os.environ.get(Key.REFRESH_TOKEN)
        self.id_token = os.environ.get(Key.ID_TOKEN)

    def get_refresh_token(self, mailaddress: str, password: str) -> str:
        """Gets a refresh token and saves it to the .env file.

        Args:
            mailaddress: The user's email address.
            password: The user's password.

        Returns:
            The new refresh token.

        Raises:
            httpx.HTTPStatusError: If the API request fails.
        """
        body = {"mailaddress": mailaddress, "password": password}
        resp = self.client.post("/token/auth_user", json=body)
        resp.raise_for_status()

        refresh_token = resp.json()["refreshToken"]
        dotenv_path = find_dotenv() or ".env"
        set_key(dotenv_path, Key.REFRESH_TOKEN, refresh_token)
        return refresh_token

    def get_id_token(self, refresh_token: str) -> str:
        """Gets an ID token and saves it to the .env file.

        Args:
            refresh_token: The refresh token to use for getting
                a new ID token.

        Returns:
            The new ID token.

        Raises:
            httpx.HTTPStatusError: If the API request fails.
        """
        url = f"/token/auth_refresh?refreshtoken={refresh_token}"
        resp = self.client.post(url)
        resp.raise_for_status()

        id_token = resp.json()["idToken"]
        dotenv_path = find_dotenv() or ".env"
        set_key(dotenv_path, Key.ID_TOKEN, id_token)
        return id_token
