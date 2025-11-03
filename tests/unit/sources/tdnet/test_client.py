from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import polars as pl
import pytest
from httpx import HTTPStatusError, Response
from polars.testing import assert_frame_equal

from kabukit.sources.tdnet.client import TdnetClient
from kabukit.sources.tdnet.parser import Item

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


async def test_get_dates(mocker: MockerFixture) -> None:
    mock_get = mocker.patch.object(TdnetClient, "get")
    mock_get.return_value = Response(200, text="abc")

    mock_iter_dates = mocker.patch(
        "kabukit.sources.tdnet.client.iter_dates",
        return_value=iter([1, 2]),
    )

    client = TdnetClient()
    dates = await client.get_dates()

    assert dates == [1, 2]
    mock_get.assert_awaited_once_with("I_main_00.html")
    mock_iter_dates.assert_called_once_with("abc")


@pytest.mark.parametrize("date", ["20230101", datetime.date(2023, 1, 1)])
async def test_get_page(mocker: MockerFixture, date: str | datetime.date) -> None:
    mock_get = mocker.patch.object(TdnetClient, "get")
    mock_get.return_value = Response(200, text="test_html")

    client = TdnetClient()
    html = await client.get_page(date, 1)

    assert html == "test_html"
    mock_get.assert_awaited_once_with("I_list_001_20230101.html")


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


async def test_iter_items(mocker: MockerFixture) -> None:
    async def mock_iter_pages(
        self: TdnetClient,
        date: str | datetime.date,
    ) -> AsyncGenerator[str, None]:
        assert isinstance(self, TdnetClient)
        assert isinstance(date, datetime.date)
        yield "html1"
        yield "html2"

    mocker.patch.object(TdnetClient, "iter_pages", new=mock_iter_pages)
    mocker.patch(
        "kabukit.sources.tdnet.client.iter_items",
        return_value=[
            Item("1", None, datetime.time(12, 0), "A", "t1", None, None, None),
            Item("2", None, datetime.time(12, 0), "A", "t1", None, None, None),
        ],
    )

    client = TdnetClient()
    items = [item async for item in client.iter_items("20230101")]
    assert len(items) == 4
    assert all(item.disclosed_date == datetime.date(2023, 1, 1) for item in items)


async def test_get_list(mocker: MockerFixture) -> None:
    async def mock_iter_items(
        self: TdnetClient,
        date: str | datetime.date,
    ) -> AsyncGenerator[Item, None]:
        assert isinstance(self, TdnetClient)
        assert isinstance(date, str)
        yield Item("1", None, datetime.time(12, 0), "A", "t1", None, None, None)
        yield Item("2", None, datetime.time(12, 0), "A", "t1", None, None, None)

    mocker.patch.object(TdnetClient, "iter_items", new=mock_iter_items)
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
    assert_frame_equal(result, expected)


async def test_get_list_empty(mocker: MockerFixture) -> None:
    async def mock_iter_items(
        self: TdnetClient,
        date: str | datetime.date,
    ) -> AsyncGenerator[Item, None]:
        assert isinstance(self, TdnetClient)
        assert isinstance(date, str)
        for x in []:  # pyright: ignore[reportUnknownVariableType]
            yield x

    mocker.patch.object(TdnetClient, "iter_items", new=mock_iter_items)

    client = TdnetClient()
    result = await client.get_list("20230101")

    assert_frame_equal(result, pl.DataFrame())
