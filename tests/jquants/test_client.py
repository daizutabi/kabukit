"""Tests for JQuantsClient."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest

from kabukit.jquants.client import AuthKey, JQuantsClient

if TYPE_CHECKING:
    from polars import DataFrame
    from pytest_httpx import HTTPXMock
    from pytest_mock import MockerFixture

DUMMY_REFRESH_TOKEN = "dummy_refresh_token"  # noqa: S105
DUMMY_ID_TOKEN = "dummy_id_token"  # noqa: S105


def test_auth_success(httpx_mock: HTTPXMock, mocker: MockerFixture) -> None:
    """Test successful authentication process.

    Given:
        A JQuantsClient instance.
        Mocked API endpoints for successful token issuance.
        Mocked set_key function.

    When:
        client.auth() is called with dummy credentials.

    Then:
        The client's tokens are updated.
        The set_key function is called correctly to save the tokens.
    """
    # Arrange: Mock the set_key function to prevent actual file I/O
    mock_set_key = mocker.patch("kabukit.jquants.client.set_key")

    # Arrange: Mock the API responses for a successful auth flow
    httpx_mock.add_response(
        method="POST",
        url="https://api.jquants.com/v1/token/auth_user",
        json={"refreshToken": DUMMY_REFRESH_TOKEN},
        status_code=200,
    )
    httpx_mock.add_response(
        method="POST",
        url=f"https://api.jquants.com/v1/token/auth_refresh?refreshtoken={DUMMY_REFRESH_TOKEN}",
        json={"idToken": DUMMY_ID_TOKEN},
        status_code=200,
    )

    client = JQuantsClient()

    # Act
    client.auth("dummy@example.com", "dummy_password")

    # Assert: Check if the client's state is updated
    assert client.refresh_token == DUMMY_REFRESH_TOKEN
    assert client.id_token == DUMMY_ID_TOKEN

    # Assert: Check if the tokens were saved correctly
    mock_set_key.assert_any_call(
        client.dotenv_path,
        AuthKey.REFRESH_TOKEN,
        DUMMY_REFRESH_TOKEN,
    )
    mock_set_key.assert_any_call(client.dotenv_path, AuthKey.ID_TOKEN, DUMMY_ID_TOKEN)
    assert mock_set_key.call_count == 2


@pytest.fixture(scope="module")
def client() -> JQuantsClient:
    return JQuantsClient()


@pytest.fixture(scope="module")
def df_listed_info(client: JQuantsClient) -> DataFrame:
    return client.get_listed_info()


def test_listed_info_width(df_listed_info: DataFrame) -> None:
    assert df_listed_info.height > 4000
    assert 11 <= df_listed_info.width <= 13


def test_listed_info_today(df_listed_info: DataFrame) -> None:
    date = df_listed_info.item(0, "Date")
    assert isinstance(date, datetime.date)
    assert abs((date - datetime.date.today()).days) <= 3  # noqa: DTZ011


@pytest.mark.parametrize(
    ("name", "n"),
    [
        ("Sector17Code", 18),
        ("Sector17CodeName", 18),
        ("Sector33Code", 34),
        ("Sector33CodeName", 34),
        ("MarketCode", 5),
        ("MarketCodeName", 5),
    ],
)
def test_listed_info_sector17(df_listed_info: DataFrame, name: str, n: int) -> None:
    assert df_listed_info[name].n_unique() == n


@pytest.mark.parametrize(
    "sc",
    [
        "-",
        "TOPIX Small 1",
        "TOPIX Core30",
        "TOPIX Mid400",
        "TOPIX Small 2",
        "TOPIX Large70",
    ],
)
def test_listed_info_scale_category(df_listed_info: DataFrame, sc: str) -> None:
    assert sc in df_listed_info["ScaleCategory"]


@pytest.fixture(scope="module")
def date() -> datetime.date:
    today = datetime.date.today()  # noqa: DTZ011
    return today - datetime.timedelta(weeks=12)


def test_listed_info_date(client: JQuantsClient, date: datetime.date) -> None:
    df = client.get_listed_info(date=date)
    assert df.height > 4000
    df_date = df.item(0, "Date")
    assert isinstance(df_date, datetime.date)
    assert (df_date - date).days <= 7


def test_listed_info_code(client: JQuantsClient) -> None:
    df = client.get_listed_info(code="7203")
    assert df.height == 1
    name = df.item(0, "CompanyName")
    assert isinstance(name, str)
    assert "トヨタ" in name
