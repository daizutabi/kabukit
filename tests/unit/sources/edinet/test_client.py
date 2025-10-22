from __future__ import annotations

import io
import zipfile
from typing import TYPE_CHECKING

import polars as pl
import pytest
from httpx import ConnectTimeout, HTTPStatusError, Response
from polars.testing import assert_frame_equal

from kabukit.sources.edinet.client import AuthKey, EdinetClient

if TYPE_CHECKING:
    from typing import Any
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


def test_set_api_key() -> None:
    client = EdinetClient("abc")
    assert client.client.params["Subscription-Key"] == "abc"


def test_set_api_key_none_and_no_config(mocker: MockerFixture) -> None:
    mock_get_config_value = mocker.patch(
        "kabukit.sources.edinet.client.get_config_value",
        return_value=None,
    )
    client = EdinetClient()
    assert "Subscription-Key" not in client.client.params
    mock_get_config_value.assert_called_once_with(AuthKey.API_KEY)


def test_set_api_key_directly(mocker: MockerFixture) -> None:
    mock_get_config_value = mocker.patch(
        "kabukit.sources.edinet.client.get_config_value",
        return_value="should_not_be_called",
    )
    client = EdinetClient("initial_key")
    client.set_api_key("new_key")
    assert client.client.params["Subscription-Key"] == "new_key"
    mock_get_config_value.assert_not_called()


@pytest.mark.asyncio
async def test_get_success(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    expected_response = Response(200, json={"message": "success"})
    mock_get.return_value = expected_response
    expected_response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    response = await client.get("test/path", params={"a": "b"})

    assert response == expected_response
    mock_get.assert_awaited_once_with("test/path", params={"a": "b"})
    expected_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_failure(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    error_response = Response(400)
    mock_get.return_value = error_response
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
async def test_get_count_success(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"metadata": {"status": "200", "resultset": {"count": 123}}}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    count = await client.get_count("2023-10-26")

    assert count == 123
    mock_get.assert_awaited_once_with(
        "/documents.json",
        params={"date": "2023-10-26", "type": 1},
    )


@pytest.mark.asyncio
async def test_get_count_fail(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    json = {"metadata": {"status": "404", "message": "error"}}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    count = await client.get_count("2023-10-26")

    assert count == 0


@pytest.mark.asyncio
async def test_get_entries_success(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    results = [{"docID": "S100TEST"}]
    json = {"results": results}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    mock_clean_documents = mocker.patch("kabukit.sources.edinet.client.clean_entries")
    expected_df = pl.DataFrame(results)
    mock_clean_documents.return_value = expected_df

    client = EdinetClient("test_key")
    date = "2023-10-26"
    df = await client.get_list(date)

    assert_frame_equal(df, expected_df)
    mock_get.assert_awaited_once_with(
        "/documents.json",
        params={"date": date, "type": 2},
    )
    mock_clean_documents.assert_called_once()


@pytest.mark.asyncio
async def test_get_entries_no_results(
    mock_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    json = {"metadata": {"status": "200"}}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    df = await client.get_list("2023-10-26")

    assert df.is_empty()


@pytest.mark.asyncio
async def test_get_entries_empty_results(
    mock_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    json: dict[str, list[Any]] = {"results": []}
    response = Response(200, json=json)
    mock_get.return_value = response
    response.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    df = await client.get_list("2023-10-26")

    assert df.is_empty()


@pytest.mark.asyncio
async def test_get_response(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    expected_response = Response(200, content=b"file content")
    mock_get.return_value = expected_response
    mock_get.return_value.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    response = await client.get_response("S100TEST", doc_type=1)

    assert response == expected_response
    mock_get.assert_awaited_once_with("/documents/S100TEST", params={"type": 1})


@pytest.mark.asyncio
async def test_get_pdf_success(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    mock_get.return_value = Response(
        200,
        content=b"pdf content",
        headers={"content-type": "application/pdf"},
    )
    mock_get.return_value.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    df = await client.get_pdf("S100TEST")

    expected = pl.DataFrame({"docID": ["S100TEST"], "pdf": [b"pdf content"]})

    assert_frame_equal(df, expected)
    mock_get.assert_awaited_once_with("/documents/S100TEST", params={"type": 2})


@pytest.mark.asyncio
async def test_get_pdf_fail(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    mock_get.return_value = Response(
        200,
        content=b"not a pdf",
        headers={"content-type": "application/json"},
    )
    mock_get.return_value.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    msg = "PDF is not available."
    with pytest.raises(ValueError, match=msg):
        await client.get_pdf("S100TEST")


@pytest.mark.asyncio
async def test_get_zip_success(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    mock_get.return_value = Response(
        200,
        content=b"zip content",
        headers={"content-type": "application/octet-stream"},
    )
    mock_get.return_value.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    content = await client.get_zip("S100TEST", doc_type=5)

    assert content == b"zip content"
    mock_get.assert_awaited_once_with("/documents/S100TEST", params={"type": 5})


@pytest.mark.asyncio
async def test_get_zip_fail(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    mock_get.return_value = Response(
        200,
        content=b"not a zip",
        headers={"content-type": "application/json"},
    )
    mock_get.return_value.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    msg = "ZIP is not available."
    with pytest.raises(ValueError, match=msg):
        await client.get_zip("S100TEST", doc_type=5)


@pytest.mark.asyncio
async def test_get_csv_success(mock_get: AsyncMock, mocker: MockerFixture) -> None:
    csv_content = "header1\theader2\nvalue1\tvalue2"
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("test.csv", csv_content.encode("utf-16-le"))
    zip_content = zip_buffer.getvalue()

    mock_get.return_value = Response(
        200,
        content=zip_content,
        headers={"content-type": "application/octet-stream"},
    )
    mock_get.return_value.raise_for_status = mocker.MagicMock()

    mock_clean_csv = mocker.patch("kabukit.sources.edinet.client.clean_csv")
    expected_df = pl.DataFrame({"header1": ["value1"], "header2": ["value2"]})
    mock_clean_csv.return_value = expected_df

    client = EdinetClient("test_key")
    df = await client.get_csv("S100TEST")

    assert_frame_equal(df, expected_df)
    mock_get.assert_awaited_once_with("/documents/S100TEST", params={"type": 5})
    mock_clean_csv.assert_called_once()


@pytest.mark.asyncio
async def test_get_csv_no_csv_in_zip(
    mock_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("test.txt", "some text")
    zip_content = zip_buffer.getvalue()

    mock_get.return_value = Response(
        200,
        content=zip_content,
        headers={"content-type": "application/octet-stream"},
    )
    mock_get.return_value.raise_for_status = mocker.MagicMock()

    client = EdinetClient("test_key")
    msg = "CSV is not available."
    with pytest.raises(ValueError, match=msg):
        await client.get_csv("S100TEST")


@pytest.mark.asyncio
async def test_get_retries_on_failure(
    mock_get: AsyncMock,
    mocker: MockerFixture,
) -> None:
    """Test that the get method retries on retryable failures."""
    error = ConnectTimeout("Connection timed out")
    success_response = Response(200, json={"message": "success"})
    success_response.raise_for_status = mocker.MagicMock()

    mock_get.side_effect = [error, error, success_response]

    client = EdinetClient("test_key")
    response = await client.get("test/path", params={})

    assert response == success_response
    assert mock_get.call_count == 3


@pytest.mark.asyncio
async def test_get_fails_after_retries(mock_get: AsyncMock) -> None:
    """Test that the get method fails after exhausting all retries."""
    error = ConnectTimeout("Connection timed out")
    mock_get.side_effect = [error, error, error]

    client = EdinetClient("test_key")

    with pytest.raises(ConnectTimeout):
        await client.get("test/path", params={})

    assert mock_get.call_count == 3


@pytest.mark.asyncio
async def test_get_document_calls_get_csv_by_default(mocker: MockerFixture) -> None:
    client = EdinetClient("test_key")
    mock_get_csv = mocker.patch.object(client, "get_csv", new_callable=mocker.AsyncMock)
    mock_get_pdf = mocker.patch.object(client, "get_pdf", new_callable=mocker.AsyncMock)

    expected_df = pl.DataFrame({"col": ["csv_data"]})
    mock_get_csv.return_value = expected_df

    doc_id = "S100TEST"
    df = await client.get_document(doc_id)

    assert_frame_equal(df, expected_df)
    mock_get_csv.assert_awaited_once_with(doc_id)
    mock_get_pdf.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_document_calls_get_pdf_when_pdf_is_true(
    mocker: MockerFixture,
) -> None:
    client = EdinetClient("test_key")
    mock_get_csv = mocker.patch.object(client, "get_csv", new_callable=mocker.AsyncMock)
    mock_get_pdf = mocker.patch.object(client, "get_pdf", new_callable=mocker.AsyncMock)

    expected_df = pl.DataFrame({"col": ["pdf_data"]})
    mock_get_pdf.return_value = expected_df

    doc_id = "S100TEST"
    df = await client.get_document(doc_id, pdf=True)

    assert_frame_equal(df, expected_df)
    mock_get_pdf.assert_awaited_once_with(doc_id)
    mock_get_csv.assert_not_awaited()
