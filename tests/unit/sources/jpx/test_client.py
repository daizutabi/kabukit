from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx import Response

from kabukit.sources.jpx.client import SHARES_URL, JpxClient

if TYPE_CHECKING:
    from typing import Any
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture


pytestmark = pytest.mark.unit


async def test_iter_shares_html_urls(
    mock_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    html = """
    <select class="backnumber">
        <option value="/a.html">A</option>
        <option value="/b.html">B</option>
    </select>
    """
    response = Response(200, text=html)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    async with JpxClient() as client:
        html_urls = [url async for url in client.iter_shares_html_urls()]

    assert html_urls == ["/a.html", "/b.html"]
    mock_get.assert_awaited_once_with(SHARES_URL, params=None)


async def test_iter_shares_pdf_urls(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    history_html = """
    <select class="backnumber">
        <option value="/a.html">A</option>
    </select>
    """
    pdf_page_html = '<a href="/HP-2023.10.pdf">PDF</a>'

    def side_effect(url: str, **_kwargs: Any) -> Response:
        if url == SHARES_URL:
            res = Response(200, text=history_html)
        elif url == "/a.html":
            res = Response(200, text=pdf_page_html)
        else:
            res = Response(404)
        res.raise_for_status = mocker.MagicMock()
        return res

    mock_get.side_effect = side_effect

    async with JpxClient() as client:
        pdf_urls = [link async for link in client.iter_shares_pdf_urls()]

    assert pdf_urls == ["/HP-2023.10.pdf"]
    assert mock_get.call_count == 2
    mock_get.assert_any_await(SHARES_URL, params=None)
    mock_get.assert_any_await("/a.html", params=None)


async def test_iter_shares_pdf_urls_with_html_url(
    mock_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    pdf_page_html = '<a href="/HP-2023.10.pdf">PDF</a>'
    response = Response(200, text=pdf_page_html)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    async with JpxClient() as client:
        pdf_urls = [link async for link in client.iter_shares_pdf_urls("/a.html")]

    assert pdf_urls == ["/HP-2023.10.pdf"]
    assert mock_get.call_count == 1
    mock_get.assert_awaited_once_with("/a.html", params=None)


async def test_get_shares(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    response = Response(200, content=b"abc")
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    mock_parse_shares = mocker.patch(
        "kabukit.sources.jpx.client.parse_shares",
        return_value=mocker.MagicMock(),
    )

    async with JpxClient() as client:
        await client.get_shares("/a.pdf")

    mock_get.assert_awaited_once_with("/a.pdf", params=None)
    mock_parse_shares.assert_called_once_with(b"abc")
