from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from httpx import HTTPStatusError
from polars import DataFrame

from kabukit.sources.jquants.client import JQuantsClient

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.system

is_auth_set = bool(os.getenv("JQUANTS_MAILADDRESS") and os.getenv("JQUANTS_PASSWORD"))
reason = "JQUANTS_MAILADDRESS and JQUANTS_PASSWORD must be set"


@pytest.mark.skipif(not is_auth_set, reason=reason)
@pytest.mark.asyncio
async def test_auth_from_config(client: JQuantsClient) -> None:
    id_token = await client.auth()
    assert id_token is not None


@pytest.mark.skipif(not is_auth_set, reason=reason)
@pytest.mark.asyncio
async def test_auth_from_args(client: JQuantsClient) -> None:
    mailaddress = os.getenv("JQUANTS_MAILADDRESS")
    password = os.getenv("JQUANTS_PASSWORD")
    id_token = await client.auth(mailaddress, password)
    assert id_token is not None


@pytest.mark.asyncio
async def test_auth_invalid(client: JQuantsClient) -> None:
    with pytest.raises(HTTPStatusError):
        await client.auth("invalid_email", "invalid_password")


@pytest.mark.skipif(not is_auth_set, reason=reason)
@pytest.mark.asyncio
async def test_auth_and_reread_from_config(
    client: JQuantsClient,
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    from kabukit.sources.jquants.client import AuthKey
    from kabukit.utils.config import save_config_key

    mocker.patch(
        "kabukit.utils.config.get_config_path",
        return_value=tmp_path / "config.toml",
    )

    id_token = await client.auth()
    assert id_token is not None

    save_config_key(AuthKey.ID_TOKEN, id_token)

    client = JQuantsClient()
    assert id_token in client.client.headers["Authorization"]
    assert id_token in (tmp_path / "config.toml").read_text()


@pytest.mark.skipif(not is_auth_set, reason=reason)
@pytest.mark.asyncio
async def test_auth_and_get_data(client: JQuantsClient) -> None:
    id_token = await client.auth()
    assert id_token is not None

    df = await client.get_info(code="80310")
    assert isinstance(df, DataFrame)
    assert not df.is_empty()


@pytest.mark.skipif(
    is_auth_set,
    reason="JQUANTS_MAILADDRESS and JQUANTS_PASSWORD are set",
)
@pytest.mark.asyncio
async def test_auth_error(client: JQuantsClient) -> None:
    with pytest.raises(ValueError, match="メールアドレス"):
        await client.auth()
