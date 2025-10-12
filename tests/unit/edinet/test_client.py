from __future__ import annotations

import io
import zipfile
from typing import TYPE_CHECKING

import polars as pl
import pytest
from httpx import ConnectTimeout, HTTPStatusError, Response
from polars.testing import assert_frame_equal

from kabukit.edinet.client import AuthKey, EdinetClient

if TYPE_CHECKING:
    from typing import Any
    from unittest.mock import AsyncMock, MagicMock

    from pytest_mock import MockerFixture


def test_set_api_key() -> None:
    client = EdinetClient("abc")
    assert client.client.params["Subscription-Key"] == "abc"


def test_set_api_key_none(mocker: MockerFixture) -> None:
    mocker.patch.dict("os.environ", {AuthKey.API_KEY: "def"})
    client = EdinetClient()
    assert client.client.params["Subscription-Key"] == "def"


@pytest.fixture
def async_client(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("kabukit.core.client.AsyncClient").return_value


@pytest.fixture
def get(async_client: MagicMock, mocker: MockerFixture) -> AsyncMock:
    get = mocker.AsyncMock()
    async_client.get = get
    return get


@pytest.mark.asyncio
async def test_get_success(get: AsyncMock, mocker: MockerFixture) -> None:
    expected_response = Response(200, json={"message": "success"})
    get.return_value = expected_response
    expected_response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    response = await client.get("test/path", params={"a": "b"})

    assert response == expected_response
    get.assert_awaited_once_with("test/path", params={"a": "b"})
    expected_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_failure(get: AsyncMock, mocker: MockerFixture) -> None:
    error_response = Response(400)
    get.return_value = error_response
    error_response.raise_for_status = mocker.MagicMock(
        side_effect=HTTPStatusError(
            "Bad Request",
            request=mocker.MagicMock(),
            response=error_response,
        ),
    )

    client = EdinetClient("test_key")

    with pytest.raises(HTTPStatusError):
        await client.get("test/path", params={})

    error_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_count_success(get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"metadata": {"status": "200", "resultset": {"count": 123}}}
    response = Response(200, json=json)
    get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    count = await client.get_count("2023-10-26")

    assert count == 123
    get.assert_awaited_once_with(
        "/documents.json",
        params={"date": "2023-10-26", "type": 1},
    )


@pytest.mark.asyncio
async def test_get_count_fail(get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"metadata": {"status": "404", "message": "error"}}
    response = Response(200, json=json)
    get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    count = await client.get_count("2023-10-26")

    assert count == 0


@pytest.mark.asyncio
async def test_get_documents_success(get: AsyncMock, mocker: MockerFixture) -> None:
    results = [{"docID": "S100TEST"}]
    json = {"results": results}
    response = Response(200, json=json)
    get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    mock_clean_documents = mocker.patch("kabukit.edinet.client.clean_documents")
    expected_df = pl.DataFrame(results)
    mock_clean_documents.return_value = expected_df

    client = EdinetClient("test_key")
    date = "2023-10-26"
    df = await client.get_documents(date)

    assert_frame_equal(df, expected_df)
    get.assert_awaited_once_with(
        "/documents.json",
        params={"date": date, "type": 2},
    )
    mock_clean_documents.assert_called_once()


@pytest.mark.asyncio
async def test_get_documents_no_results(get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"metadata": {"status": "200"}}
    response = Response(200, json=json)
    get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    df = await client.get_documents("2023-10-26")

    assert df.is_empty()


@pytest.mark.asyncio
async def test_get_documents_empty_results(
    get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    json: dict[str, list[Any]] = {"results": []}
    response = Response(200, json=json)
    get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    df = await client.get_documents("2023-10-26")

    assert df.is_empty()


@pytest.mark.asyncio
async def test_get_document(get: AsyncMock, mocker: MockerFixture) -> None:
    expected_response = Response(200, content=b"file content")
    get.return_value = expected_response
    get.return_value.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    response = await client.get_document("S100TEST", doc_type=1)

    assert response == expected_response
    get.assert_awaited_once_with("/documents/S100TEST", params={"type": 1})


@pytest.mark.asyncio
async def test_get_pdf_success(get: AsyncMock, mocker: MockerFixture) -> None:
    get.return_value = Response(
        200,
        content=b"pdf content",
        headers={"content-type": "application/pdf"},
    )
    get.return_value.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    content = await client.get_pdf("S100TEST")

    assert content == b"pdf content"
    get.assert_awaited_once_with("/documents/S100TEST", params={"type": 2})


@pytest.mark.asyncio
async def test_get_pdf_fail(get: AsyncMock, mocker: MockerFixture) -> None:
    get.return_value = Response(
        200,
        content=b"not a pdf",
        headers={"content-type": "application/json"},
    )
    get.return_value.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    msg = "PDF is not available."
    with pytest.raises(ValueError, match=msg):
        await client.get_pdf("S100TEST")


@pytest.mark.asyncio
async def test_get_zip_success(get: AsyncMock, mocker: MockerFixture) -> None:
    get.return_value = Response(
        200,
        content=b"zip content",
        headers={"content-type": "application/octet-stream"},
    )
    get.return_value.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    content = await client.get_zip("S100TEST", doc_type=5)

    assert content == b"zip content"
    get.assert_awaited_once_with("/documents/S100TEST", params={"type": 5})


@pytest.mark.asyncio
async def test_get_zip_fail(get: AsyncMock, mocker: MockerFixture) -> None:
    get.return_value = Response(
        200,
        content=b"not a zip",
        headers={"content-type": "application/json"},
    )
    get.return_value.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    msg = "ZIP is not available."
    with pytest.raises(ValueError, match=msg):
        await client.get_zip("S100TEST", doc_type=5)


@pytest.mark.asyncio
async def test_get_csv_success(get: AsyncMock, mocker: MockerFixture) -> None:
    csv_content = "header1\theader2\nvalue1\tvalue2"
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("test.csv", csv_content.encode("utf-16-le"))
    zip_content = zip_buffer.getvalue()

    get.return_value = Response(
        200,
        content=zip_content,
        headers={"content-type": "application/octet-stream"},
    )
    get.return_value.raise_for_status = mocker.MagicMock()

    mock_clean_csv = mocker.patch("kabukit.edinet.client.clean_csv")
    expected_df = pl.DataFrame({"header1": ["value1"], "header2": ["value2"]})
    mock_clean_csv.return_value = expected_df

    client = EdinetClient("test_key")
    df = await client.get_csv("S100TEST")

    assert_frame_equal(df, expected_df)
    get.assert_awaited_once_with("/documents/S100TEST", params={"type": 5})
    mock_clean_csv.assert_called_once()


@pytest.mark.asyncio
async def test_get_csv_no_csv_in_zip(get: AsyncMock, mocker: MockerFixture) -> None:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("test.txt", "some text")
    zip_content = zip_buffer.getvalue()

    get.return_value = Response(
        200,
        content=zip_content,
        headers={"content-type": "application/octet-stream"},
    )
    get.return_value.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    msg = "CSV is not available."
    with pytest.raises(ValueError, match=msg):
        await client.get_csv("S100TEST")


@pytest.mark.asyncio
async def test_get_retries_on_failure(get: AsyncMock, mocker: MockerFixture) -> None:
    """Test that the get method retries on retryable failures."""
    error = ConnectTimeout("Connection timed out")
    success_response = Response(200, json={"message": "success"})
    success_response.raise_for_status = mocker.MagicMock()

    get.side_effect = [error, error, success_response]

    client = EdinetClient("test_key")
    response = await client.get("test/path", params={})

    assert response == success_response
    assert get.call_count == 3


@pytest.mark.asyncio
async def test_get_fails_after_retries(get: AsyncMock) -> None:
    """Test that the get method fails after exhausting all retries."""
    error = ConnectTimeout("Connection timed out")
    get.side_effect = [error, error, error]

    client = EdinetClient("test_key")

    with pytest.raises(ConnectTimeout):
        await client.get("test/path", params={})

    assert get.call_count == 3
