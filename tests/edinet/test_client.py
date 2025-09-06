def test_get() -> None:
    from kabukit.edinet.client import EdinetClient

    client = EdinetClient()
    response = client.get("/documents.json", {"date": "2025-09-05", "type": 2})
    print(response)
    assert response is not None
    assert 0
