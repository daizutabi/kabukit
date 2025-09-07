from __future__ import annotations

import os
from enum import StrEnum
from typing import TYPE_CHECKING

import polars as pl
from httpx import AsyncClient
from polars import DataFrame

from kabukit.config import load_dotenv, set_key
from kabukit.params import get_params

if TYPE_CHECKING:
    import datetime
    from collections.abc import AsyncIterator
    from typing import Any

    from httpx import HTTPStatusError  # noqa: F401
    from httpx._types import QueryParamTypes

API_VERSION = "v1"
BASE_URL = f"https://api.jquants.com/{API_VERSION}"


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

    client: AsyncClient

    def __init__(self) -> None:
        load_dotenv()
        client = AsyncClient(base_url=BASE_URL)

        if id_token := os.environ.get(AuthKey.ID_TOKEN):
            client.headers["Authorization"] = f"Bearer {id_token}"

        self.client = client

    async def aclose(self) -> None:
        await self.client.aclose()

    async def auth(self, mailaddress: str, password: str) -> None:
        """Authenticate and save tokens.

        Args:
            mailaddress: The user's email address.
            password: The user's password.

        Raises:
            HTTPStatusError: If any API request fails.
        """
        refresh_token = await self.get_refresh_token(mailaddress, password)
        id_token = await self.get_id_token(refresh_token)
        set_key(AuthKey.REFRESH_TOKEN, refresh_token)
        set_key(AuthKey.ID_TOKEN, id_token)

    async def post(self, url: str, json: Any | None = None) -> Any:
        """Send a POST request to the specified URL.

        Args:
            url: The URL path for the POST request.
            json: The JSON payload for the request body.

        Returns:
            The JSON response from the API.

        Raises:
            HTTPStatusError: If the API request fails.
        """
        resp = await self.client.post(url, json=json)
        resp.raise_for_status()
        return resp.json()

    async def get_refresh_token(self, mailaddress: str, password: str) -> str:
        """Get a new refresh token from the API.

        Args:
            mailaddress: The user's email address.
            password: The user's password.

        Returns:
            The new refresh token.

        Raises:
            httpx.HTTPStatusError: If the API request fails.
        """
        json_data = {"mailaddress": mailaddress, "password": password}
        data = await self.post("/token/auth_user", json=json_data)
        return data["refreshToken"]

    async def get_id_token(self, refresh_token: str) -> str:
        """Get a new ID token from the API.

        Args:
            refresh_token: The refresh token to use.

        Returns:
            The new ID token.

        Raises:
            HTTPStatusError: If the API request fails.
        """
        url = f"/token/auth_refresh?refreshtoken={refresh_token}"
        data = await self.post(url)
        return data["idToken"]

    async def get(self, url: str, params: QueryParamTypes | None = None) -> Any:
        """Send a GET request to the specified URL.

        Args:
            url: The URL path for the GET request.
            params: The query parameters for the request.

        Returns:
            The JSON response from the API.

        Raises:
            HTTPStatusError: If the API request fails.
        """
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_info(
        self,
        code: str | None = None,
        date: str | datetime.date | None = None,
    ) -> DataFrame:
        """Get listed info (e.g., stock details) from the API.

        Args:
            code (str | None): The stock code to filter by.
            date: Optional. The date to filter by (YYYY-MM-DD format
                or datetime.date object).

        Returns:
            A Polars DataFrame containing the listed info.

        Raises:
            AuthenticationError: If no ID token is available.
            HTTPStatusError: If the API request fails.
        """
        params = get_params(code=code, date=date)
        url = "/listed/info"
        data = await self.get(url, params)
        df = DataFrame(data["info"])
        return df.with_columns(pl.col("Date").str.to_date())

    async def iter_pages(
        self,
        url: str,
        params: dict[str, Any] | None,
        name: str,
    ) -> AsyncIterator[DataFrame]:
        """Iterate through paginated API responses.

        Args:
            url: The base URL for the API endpoint.
            params: Optional. Dictionary of query parameters.
            name: The key in the JSON response containing the list of items.

        Yields:
            A Polars DataFrame for each page of data.

        Raises:
            AuthenticationError: If no ID token is available.
            HTTPStatusError: If the API request fails.
        """
        params = params or {}

        while True:
            data = await self.get(url, params)
            yield DataFrame(data[name])
            if "pagination_key" in data:
                params["pagination_key"] = data["pagination_key"]
            else:
                break

    async def get_prices(
        self,
        code: str | None = None,
        date: str | datetime.date | None = None,
        from_: str | datetime.date | None = None,
        to: str | datetime.date | None = None,
    ) -> DataFrame:
        """Get daily stock prices from the API.

        Args:
            code: Optional. The stock code to filter by.
            date: Optional. The specific date for which to retrieve prices.
                Cannot be used with `from_` or `to`.
            from_: Optional. The start date for a price range.
                Requires `to` if `date` is not specified.
            to: Optional. The end date for a price range.
                Requires `from_` if `date` is not specified.

        Returns:
            A Polars DataFrame containing daily stock prices.

        Raises:
            ValueError: If both `date` and `from_`/`to` are specified.
            AuthenticationError: If no ID token is available.
            HTTPStatusError: If the API request fails.
        """
        if date and (from_ or to):
            msg = "Cannot specify both date and from/to parameters."
            raise ValueError(msg)

        params = get_params(code=code, date=date, from_=from_, to=to)

        url = "/prices/daily_quotes"
        name = "daily_quotes"

        dfs = [df async for df in self.iter_pages(url, params, name)]
        df = pl.concat(dfs)
        if df.is_empty():
            return df

        return df.with_columns(pl.col("Date").str.to_date())

    async def get_statements(
        self,
        code: str | None = None,
        date: str | datetime.date | None = None,
    ) -> DataFrame:
        """Get financial statements from the API.

        Args:
            code: Optional. The stock code to filter by.
            date: Optional. The date to filter by (YYYY-MM-DD format
                or datetime.date object).

        Returns:
            A Polars DataFrame containing the financial statements.

        Raises:
            AuthenticationError: If no ID token is available.
            HTTPStatusError: If the API request fails.
        """
        params = get_params(code=code, date=date)
        url = "/fins/statements"
        name = "statements"

        dfs = [df async for df in self.iter_pages(url, params, name)]
        df = pl.concat(dfs)
        if df.is_empty():
            return df

        return df.with_columns(pl.col("DisclosedDate").str.to_date().alias("Date"))

    async def get_announcement(self) -> DataFrame:
        """Get financial announcement from the API.

        Returns:
            A Polars DataFrame containing the financial announcement.

        Raises:
            AuthenticationError: If no ID token is available.
            HTTPStatusError: If the API request fails.
        """
        url = "fins/announcement"
        name = "announcement"

        dfs = [df async for df in self.iter_pages(url, {}, name)]
        df = pl.concat(dfs)
        if df.is_empty():
            return df

        return df.with_columns(pl.col("Date").str.to_date())

    async def get_trades_spec(
        self,
        section: str | None = None,
        from_: str | datetime.date | None = None,
        to: str | datetime.date | None = None,
    ) -> DataFrame:
        """Get trading specification from the API.

        Args:
            section: Optional. The section to filter by.
            from_: Optional. The start date for a range.
            to: Optional. The end date for a range.

        Returns:
            A Polars DataFrame containing the trading specification.

        Raises:
            AuthenticationError: If no ID token is available.
            HTTPStatusError: If the API request fails.
        """
        params = get_params(section=section, from_=from_, to=to)

        url = "/markets/trades_spec"
        name = "trades_spec"

        dfs = [df async for df in self.iter_pages(url, params, name)]
        df = pl.concat(dfs)
        if df.is_empty():
            return df

        return df.with_columns(
            pl.col(name).str.to_date()
            for name in ["PublishedDate", "StartDate", "EndDate"]
        )
