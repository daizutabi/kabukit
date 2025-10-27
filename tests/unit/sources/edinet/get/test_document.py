from __future__ import annotations

import io
import zipfile
from typing import TYPE_CHECKING

import polars as pl
import pytest
from httpx import Response
from polars.testing import assert_frame_equal

from kabukit.sources.edinet.client import EdinetClient

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


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

    expected = pl.DataFrame(
        {"DocumentId": ["S100TEST"], "PdfContent": [b"pdf content"]},
    )

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

    mock_transform_csv = mocker.patch("kabukit.sources.edinet.client.transform_csv")
    expected_df = pl.DataFrame({"header1": ["value1"], "header2": ["value2"]})
    mock_transform_csv.return_value = expected_df

    client = EdinetClient("test_key")
    df = await client.get_csv("S100TEST")

    assert_frame_equal(df, expected_df)
    mock_get.assert_awaited_once_with("/documents/S100TEST", params={"type": 5})
    mock_transform_csv.assert_called_once()


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
