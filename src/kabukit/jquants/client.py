"""This module provides a client for the J-Quants API.

It handles authentication and provides methods to interact with
the API endpoints.
"""

from __future__ import annotations

import os
from enum import StrEnum

from dotenv import find_dotenv, load_dotenv, set_key
from httpx import Client, HTTPStatusError  # noqa: F401

API_VERSION = "v1"


class Key(StrEnum):
    """Environment variable keys for J-Quants authentication."""

    REFRESH_TOKEN = "JQUANTS_REFRESH_TOKEN"  # noqa: S105
    ID_TOKEN = "JQUANTS_ID_TOKEN"  # noqa: S105


class JQuantsClient:
    """A client for interacting with the J-Quants API.

    This client manages API authentication tokens (refresh and ID)
    and provides methods to access various J-Quants API
    endpoints. Tokens are loaded from environment variables.
    Use `save_token` to persist them to a .env file.

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

        It sets up the httpx client, loads authentication tokens
        from environment variables, and sets the auth header if an
        ID token is present.
        """
        self.client = Client(base_url=f"https://api.jquants.com/{API_VERSION}")

        load_dotenv()
        self.refresh_token = os.environ.get(Key.REFRESH_TOKEN)
        self.id_token = os.environ.get(Key.ID_TOKEN)
        self.set_header()

    def set_header(self) -> None:
        """Sets the Authorization header if an ID token is available."""
        if self.id_token:
            self.client.headers["Authorization"] = f"Bearer {self.id_token}"

    def auth(self, mailaddress: str, password: str) -> None:
        """Authenticates, saves tokens, and sets the auth header.

        This method orchestrates the entire authentication process:

        1. Gets a new refresh token.
        2. Gets a new ID token using the refresh token.
        3. Saves both tokens to the .env file.
        4. Sets the Authorization header for subsequent requests.

        Args:
            mailaddress: The user's email address.
            password: The user's password.

        Raises:
            HTTPStatusError: If any API request fails.
        """
        self.refresh_token = self.get_refresh_token(mailaddress, password)
        self.id_token = self.get_id_token(self.refresh_token)
        self.save_token(Key.REFRESH_TOKEN, self.refresh_token)
        self.save_token(Key.ID_TOKEN, self.id_token)
        self.set_header()

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
        body = {"mailaddress": mailaddress, "password": password}
        resp = self.client.post("/token/auth_user", json=body)
        resp.raise_for_status()
        return resp.json()["refreshToken"]

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
        resp = self.client.post(url)
        resp.raise_for_status()
        return resp.json()["idToken"]

    def save_token(self, key: Key, value: str) -> None:
        """Saves a token to the .env file.

        Args:
            key: The key of the token to save (e.g., Key.REFRESH_TOKEN).
            value: The token value to save.
        """
        dotenv_path = find_dotenv() or ".env"
        set_key(dotenv_path, key, value)
