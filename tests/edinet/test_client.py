from pydoc import cli

import pytest

from kabukit.edinet.client import EdinetClient


@pytest.fixture(scope="module")
def client() -> EdinetClient:
    return EdinetClient()


def test_count(client: EdinetClient) -> None:
    assert client.get_count("2025-09-05") > 0


def test_count_zero(client: EdinetClient) -> None:
    assert client.get_count("1000-01-01") == 0


def test_list(client: EdinetClient) -> None:
    count = client.get_count("2025-09-04")
    df = client.get_list("2025-09-04")
    assert df.shape == (count, 29)


def test_list_zero(client: EdinetClient) -> None:
    df = client.get_list("1000-01-01")
    assert df.shape == (0, 0)


def test_document(client: EdinetClient) -> None:
    df = client.get_list("2025-09-04")
    doc_id = df.item(0, "docID")
    data = client.get_document(doc_id, type=1)
    print(data)
    assert 0
