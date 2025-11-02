from __future__ import annotations

import random

import pytest
import pytest_asyncio

from kabukit.sources.jpx.client import JpxClient
from kabukit.sources.jpx.parser import iter_shares_links, iter_shares_urls

pytestmark = pytest.mark.system


async def test_iter_shares_urls(client: JpxClient) -> None:
    response = await client.get("/listing/co/01.html")
    for k, url in enumerate(iter_shares_urls(response.text)):
        if k == 0:
            assert url == "/listing/co/01.html"
        else:
            assert url == f"/listing/co/01-archives-0{k}.html"


@pytest.fixture(
    params=[
        "/listing/co/01.html",
        "/listing/co/01-archives-01.html",
        "/listing/co/01-archives-02.html",
    ],
)
def shares_url(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest_asyncio.fixture
async def shares_text(client: JpxClient, shares_url: str) -> str:
    response = await client.get(shares_url)
    return response.text


def test_iter_shares_links(shares_text: str) -> None:
    links = list(iter_shares_links(shares_text))
    assert 1 <= len(links) <= 12


@pytest_asyncio.fixture(scope="module")
async def shares_links() -> list[str]:
    async with JpxClient() as client:
        links = [link async for link in client._iter_shares_links()]  # noqa: SLF001
        random.shuffle(links)
        return links


@pytest_asyncio.fixture(scope="module", params=range(3))
async def shares_link(shares_links: list[str], request: pytest.FixtureRequest) -> str:
    assert isinstance(request.param, int)
    return shares_links[request.param]


@pytest_asyncio.fixture(scope="module")
async def shares_pdf(shares_link: str) -> bytes:
    async with JpxClient() as client:
        response = await client.get(shares_link)
        return response.content


def test_shares_pdf_content(shares_pdf: bytes) -> None:
    assert shares_pdf.startswith(b"%PDF-1.")
