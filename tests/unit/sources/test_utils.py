from __future__ import annotations

import io
import re
import zipfile

import pytest
from bs4 import BeautifulSoup, Tag

from kabukit.sources.utils import get_soup, iter_contents


def test_get_soup_basic() -> None:
    html = "<html><head><title>Test</title></head><body><p>Hello</p></body></html>"
    soup = get_soup(html)
    assert isinstance(soup, BeautifulSoup)
    assert soup.title
    assert soup.title.string == "Test"
    assert isinstance(soup.p, Tag)
    assert soup.p.string == "Hello"


def test_get_soup_cache() -> None:
    html = "<html><body><p>Cache me</p></body></html>"
    soup1 = get_soup(html)
    soup2 = get_soup(html)
    assert soup1 is soup2
    # Clear cache to avoid side effects on other tests
    get_soup.cache_clear()


def test_get_soup_cache_different_html() -> None:
    html1 = "<html><body><p>First</p></body></html>"
    html2 = "<html><body><p>Second</p></body></html>"
    soup1 = get_soup(html1)
    soup2 = get_soup(html2)
    assert soup1 is not soup2
    get_soup.cache_clear()


@pytest.fixture
def dummy_zip_content() -> bytes:
    """Creates a dummy zip file in memory for testing."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("test.txt", b"hello")
        zf.writestr("data/other.txt", b"world")
        zf.writestr("image.jpg", b"not text")
    return buffer.getvalue()


def test_iter_contents_single_match(dummy_zip_content: bytes) -> None:
    pattern = re.compile(r"test\.txt")
    result = list(iter_contents(dummy_zip_content, pattern))
    assert result == [b"hello"]


def test_iter_contents_multiple_matches(dummy_zip_content: bytes) -> None:
    pattern = re.compile(r".*\.txt")
    result = list(iter_contents(dummy_zip_content, pattern))
    # Use set to ignore order of files in zip
    assert set(result) == {b"hello", b"world"}


def test_iter_contents_no_match(dummy_zip_content: bytes) -> None:
    pattern = re.compile(r"no_such_file\.dat")
    result = list(iter_contents(dummy_zip_content, pattern))
    assert result == []


def test_iter_contents_with_filename(dummy_zip_content: bytes) -> None:
    pattern = re.compile(r".*\.txt")
    result = list(iter_contents(dummy_zip_content, pattern, include_filename=True))
    # Use set to ignore order of files in zip
    assert set(result) == {("test.txt", b"hello"), ("data/other.txt", b"world")}


def test_iter_contents_with_filename_single_match(dummy_zip_content: bytes) -> None:
    pattern = re.compile(r"test\.txt")
    result = list(iter_contents(dummy_zip_content, pattern, include_filename=True))
    assert result == [("test.txt", b"hello")]


def test_iter_contents_empty_zip() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w"):
        pass
    empty_zip_content = buffer.getvalue()

    pattern = re.compile(r".*")
    result_without_filename = list(iter_contents(empty_zip_content, pattern))
    result_with_filename = list(
        iter_contents(empty_zip_content, pattern, include_filename=True),
    )

    assert result_without_filename == []
    assert result_with_filename == []
