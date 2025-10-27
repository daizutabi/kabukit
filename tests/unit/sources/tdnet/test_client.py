from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import polars as pl
import pytest
from httpx import HTTPStatusError, Response
from polars.testing import assert_frame_equal

from kabukit.sources.tdnet.client import TdnetClient

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_dates(mocker: MockerFixture) -> None:
    text = """
    <select name="daylist">
        <option value="I_list_001_20230101.html">2023/01/01</option>
        <option value="I_list_001_20230102.html">2023/01/02</option>
    </select>
    """
    mock_get = mocker.patch.object(TdnetClient, "get")
    mock_get.return_value = Response(200, text=text)

    client = TdnetClient()
    dates = await client.get_dates()

    assert dates == [datetime.date(2023, 1, 1), datetime.date(2023, 1, 2)]
    mock_get.assert_awaited_once_with("I_main_00.html")


@pytest.mark.asyncio
async def test_get_dates_no_daylist(mocker: MockerFixture) -> None:
    mock_get = mocker.patch.object(TdnetClient, "get")
    mock_get.return_value = Response(200, text="<html></html>")

    client = TdnetClient()
    dates = await client.get_dates()

    assert dates == []


@pytest.mark.asyncio
@pytest.mark.parametrize("date", ["20230101", datetime.date(2023, 1, 1)])
async def test_get_page(mocker: MockerFixture, date: str | datetime.date) -> None:
    mock_get = mocker.patch.object(TdnetClient, "get")
    mock_get.return_value = Response(200, text="test_html")

    client = TdnetClient()
    html = await client.get_page(date, 1)

    assert html == "test_html"
    mock_get.assert_awaited_once_with("I_list_001_20230101.html")


@pytest.mark.asyncio
async def test_iter_pages(mocker: MockerFixture) -> None:
    mocker.patch(
        "kabukit.sources.tdnet.client.iter_page_numbers",
        return_value=iter([1, 2]),
    )
    mock_get_page = mocker.patch.object(TdnetClient, "get_page")
    mock_get_page.side_effect = ["html1", "html2"]

    client = TdnetClient()
    pages = [p async for p in client.iter_pages("20230101")]

    assert pages == ["html1", "html2"]
    assert mock_get_page.call_count == 2


@pytest.mark.asyncio
async def test_iter_pages_http_error(mocker: MockerFixture) -> None:
    mocker.patch.object(
        TdnetClient,
        "get_page",
        side_effect=HTTPStatusError(
            "error",
            request=mocker.MagicMock(),
            response=mocker.MagicMock(),
        ),
    )
    client = TdnetClient()
    pages = [p async for p in client.iter_pages("20230101")]
    assert pages == []


@pytest.mark.asyncio
async def test_get_list(mocker: MockerFixture) -> None:
    async def mock_iter_pages(
        self: TdnetClient,
        date: str | datetime.date,
    ) -> AsyncGenerator[str, None]:
        assert isinstance(self, TdnetClient)
        assert isinstance(date, datetime.date)
        yield "html1"
        yield "html2"

    mocker.patch.object(TdnetClient, "iter_pages", new=mock_iter_pages)
    mock_parse = mocker.patch(
        "kabukit.sources.tdnet.client.parse",
        side_effect=[pl.DataFrame({"a": [1]}), pl.DataFrame({"a": [2]})],
    )
    mock_transform_list = mocker.patch(
        "kabukit.sources.tdnet.client.transform_list",
        return_value=pl.DataFrame({"a": [3]}),
    )
    mock_with_date = mocker.patch(
        "kabukit.sources.tdnet.client.with_date",
        return_value=pl.DataFrame({"a": [4]}),
    )

    client = TdnetClient()
    result = await client.get_list("20230101")

    mock_transform_list.assert_called_once()
    mock_with_date.assert_called_once()

    expected = pl.DataFrame({"a": [4]})
    assert mock_parse.call_count == 2
    assert_frame_equal(result, expected)


@pytest.mark.asyncio
async def test_get_list_empty(mocker: MockerFixture) -> None:
    async def mock_iter_pages(
        self: TdnetClient,
        date: str | datetime.date,
    ) -> AsyncGenerator[str, None]:
        assert isinstance(self, TdnetClient)
        assert isinstance(date, datetime.date)
        yield "html1"

    mocker.patch.object(TdnetClient, "iter_pages", new=mock_iter_pages)
    mocker.patch("kabukit.sources.tdnet.client.parse", return_value=pl.DataFrame())

    client = TdnetClient()
    result = await client.get_list("20230101")

    assert result.is_empty()
