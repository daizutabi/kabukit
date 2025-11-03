from __future__ import annotations

import itertools
import random
import re

import polars as pl
import pytest
import pytest_asyncio

from kabukit.sources.jpx.client import JpxClient
from kabukit.sources.jpx.parser import (
    iter_shares,
    iter_shares_html_urls,
    iter_shares_pages,
    iter_shares_pdf_urls,
    parse_shares,
)

pytestmark = pytest.mark.system


async def test_iter_shares_html_urls(client: JpxClient) -> None:
    response = await client.get("/listing/co/01.html")
    for k, url in enumerate(iter_shares_html_urls(response.text)):
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
async def shares_html(client: JpxClient, shares_url: str) -> str:
    response = await client.get(shares_url)
    return response.text


def test_iter_shares_links(shares_html: str) -> None:
    links = list(iter_shares_pdf_urls(shares_html))
    assert 1 <= len(links) <= 12


@pytest_asyncio.fixture(scope="module")
async def shares_pdf_urls() -> list[str]:
    async with JpxClient() as client:
        links = [link async for link in client.iter_shares_pdf_urls()]
        random.shuffle(links)
        return links


@pytest_asyncio.fixture(scope="module", params=range(3))
async def shares_pdf_url(
    shares_pdf_urls: list[str],
    request: pytest.FixtureRequest,
) -> str:
    assert isinstance(request.param, int)
    return shares_pdf_urls[request.param]


@pytest_asyncio.fixture(scope="module")
async def shares_content(shares_pdf_url: str) -> bytes:
    async with JpxClient() as client:
        response = await client.get(shares_pdf_url)
        return response.content


def test_shares_content_starts_with_pdf(shares_content: bytes) -> None:
    assert shares_content.startswith(b"%PDF-1.")


@pytest_asyncio.fixture(scope="module")
async def shares_pages(shares_content: bytes) -> list[str]:
    it = iter_shares_pages(shares_content)
    return list(itertools.islice(it, 4))


@pytest_asyncio.fixture(scope="module", params=range(4))
async def shares_page(shares_pages: list[str], request: pytest.FixtureRequest) -> str:
    assert isinstance(request.param, int)
    return shares_pages[request.param]


def test_shares_page_starts_with_year_month(shares_page: str) -> None:
    assert re.match(r"^\s*(\d{4})年(\d{1,2})月分\n", shares_page)


def test_iter_shares(shares_page: str) -> None:
    share = next(iter_shares(shares_page))
    assert len(share.code) == 4
    assert share.year >= 2020
    assert 1 <= share.month <= 12


@pytest.fixture(scope="module")
def shares(shares_content: bytes) -> pl.DataFrame:
    return parse_shares(shares_content)


def test_parse_shares_shape(shares: pl.DataFrame) -> None:
    assert shares.width == 4
    assert shares.height > 3500


@pytest.mark.parametrize(
    ("column", "expected"),
    [
        ("Date", pl.Date),
        ("Code", pl.String),
        ("Company", pl.String),
        ("IssuedShares", pl.Int64),
    ],
)
def test_parse_shares_dtype(shares: pl.DataFrame, column: str, expected: type) -> None:
    assert shares[column].dtype == expected


@pytest.mark.parametrize("code", ["1301", "6758", "7203", "9984"])
def test_parse_shares_code(shares: pl.DataFrame, code: str) -> None:
    assert code in shares["Code"].to_list()
