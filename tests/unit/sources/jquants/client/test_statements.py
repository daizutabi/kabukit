from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any

import polars as pl
import pytest
from httpx import Response

from kabukit.sources.jquants.client import JQuantsClient

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


async def test_get_statements(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"statements": [{"Profit": 100}, {"Profit": 200}]}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_statements("123", transform=False)
    assert df["Profit"].to_list() == [100, 200]


async def test_empty(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json: dict[str, list[dict[str, str]]] = {"statements": []}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = JQuantsClient("test_token")
    df = await client.get_statements("123")
    assert df.is_empty()


async def test_error(client: JQuantsClient) -> None:
    with pytest.raises(ValueError, match="codeまたはdate"):
        await client.get_statements()


@pytest.mark.parametrize("transform_flag", [True, False])
async def test_get_transform_flag(
    mock_get: AsyncMock,
    mocker: MockerFixture,
    transform_flag: bool,
) -> None:
    def get_side_effect(url: str, params: dict[str, Any] | None = None) -> Response:  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
        if "statements" in url:
            json = {
                "statements": [
                    {"LocalCode": "7203", "DisclosedDate": "2023-01-05"},
                ],
            }
            response = Response(200, json=json)
        elif "trading_calendar" in url:
            json = {
                "trading_calendar": [
                    {"Date": "2023-01-03", "HolidayDivision": "0"},
                ],
            }
            response = Response(200, json=json)
        else:
            response = Response(404)
        response.raise_for_status = mocker.MagicMock()
        return response

    mock_get.side_effect = get_side_effect

    mock_transform = mocker.patch(
        "kabukit.sources.jquants.client.statements.transform",
        return_value=pl.DataFrame(
            {
                "Code": ["7203"],
                "DisclosedDate": [datetime.date(2023, 1, 5)],
                "DisclosedTime": [datetime.time(9, 0)],
            },
        ),
    )
    mock_with_date = mocker.patch(
        "kabukit.sources.jquants.client.with_date",
        return_value=pl.DataFrame({"Date": [datetime.date(2023, 1, 1)]}),
    )

    client = JQuantsClient("test_token")
    await client.get_statements(code="7203", transform=transform_flag)

    if transform_flag:
        mock_transform.assert_called_once()
    else:
        mock_transform.assert_not_called()

    if transform_flag:
        mock_with_date.assert_called_once()
    else:
        mock_with_date.assert_not_called()
