from unittest.mock import AsyncMock, call, patch

import pytest

from kabukit.jquants.client import AuthKey, JQuantsClient


@pytest.mark.asyncio
async def test_auth_successful_no_save():
    """Test successful authentication without saving tokens."""
    async with JQuantsClient() as client:
        # Mock the post method to simulate API responses
        client.post = AsyncMock(
            side_effect=[
                {"refreshToken": "test_refresh_token"},
                {"idToken": "test_id_token"},
            ],
        )

        # Mock set_key to avoid actual file system operations
        with patch("kabukit.jquants.client.set_key") as mock_set_key:
            # Call the auth method
            await client.auth("test@example.com", "password", save=False)

            # 1. Assert post method was called correctly
            assert client.post.call_count == 2
            # First call to get refresh token
            client.post.assert_any_call(
                "/token/auth_user",
                json={"mailaddress": "test@example.com", "password": "password"},
            )
            # Second call to get id token
            client.post.assert_any_call(
                "/token/auth_refresh?refreshtoken=test_refresh_token",
            )

            # 2. Assert that set_key was not called when save=False
            mock_set_key.assert_not_called()

            # 3. Assert that the id_token is set in the client headers
            assert client.client.headers["Authorization"] == "Bearer test_id_token"


@pytest.mark.asyncio
async def test_auth_successful_with_save():
    """Test successful authentication with saving tokens."""
    async with JQuantsClient() as client:
        # Mock the post method to simulate API responses
        client.post = AsyncMock(
            side_effect=[
                {"refreshToken": "test_refresh_token"},
                {"idToken": "test_id_token"},
            ],
        )

        # Mock set_key to avoid actual file system operations
        with patch("kabukit.jquants.client.set_key") as mock_set_key:
            # Call the auth method with save=True
            await client.auth("test@example.com", "password", save=True)

            # 1. Assert post method was called correctly (covered in the previous test)
            assert client.post.call_count == 2

            # 2. Assert that set_key was called with correct arguments
            mock_set_key.assert_has_calls(
                [
                    call(AuthKey.REFRESH_TOKEN, "test_refresh_token"),
                    call(AuthKey.ID_TOKEN, "test_id_token"),
                ],
                any_order=True,  # The order of saving tokens doesn't matter
            )

            # 3. Assert that the id_token is set in the client headers
            assert client.client.headers["Authorization"] == "Bearer test_id_token"
