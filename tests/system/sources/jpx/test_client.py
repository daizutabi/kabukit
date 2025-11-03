from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from kabukit.sources.jpx.client import JpxClient

pytestmark = pytest.mark.system


async def test_iter_shares_html_urls(client: JpxClient) -> None:
    html_urls = [url async for url in client.iter_shares_html_urls()]
    assert len(html_urls) == 6


async def test_iter_shares_pdf_urls(client: JpxClient) -> None:
    pdf_urls = [url async for url in client.iter_shares_pdf_urls()]
    assert 5 * 12 <= len(pdf_urls) <= 6 * 12


async def test_iter_shares_pdf_urls_first(client: JpxClient) -> None:
    html_urls = [url async for url in client.iter_shares_html_urls()]
    html_url = html_urls[-1]
    pdf_urls = [url async for url in client.iter_shares_pdf_urls(html_url)]
    assert len(pdf_urls) == 12


async def test_get_shares(client: JpxClient) -> None:
    pdf_url = await anext(client.iter_shares_pdf_urls())
    df = await client.get_shares(pdf_url)
    assert df.width == 4
    assert df.height > 3500
