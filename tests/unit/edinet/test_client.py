import httpx
import polars as pl
import pytest
from pytest_mock import MockerFixture

from kabukit.edinet.client import EdinetClient
from kabukit.edinet.doc import clean_csv, clean_list

# Test data for successful list response
SUCCESS_LIST_RESPONSE = {
    "metadata": {"status": "200", "resultset": {"count": 2}},
    "results": [
        {
            "docID": "S100ABC",
            "pdfFlag": "1",
            "xbrlFlag": "1",
            "csvFlag": "1",
        },
        {
            "docID": "S100DEF",
            "pdfFlag": "0",
            "xbrlFlag": "0",
            "csvFlag": "0",
        },
    ],
}

# Test data for successful count response
SUCCESS_COUNT_RESPONSE = {"metadata": {"status": "200"}, "count": 123}

# Test data for zero count response
ZERO_COUNT_RESPONSE = {"metadata": {"status": "200"}, "count": 0}

# Test data for zero list response
ZERO_LIST_RESPONSE = {"metadata": {"status": "200"}, "results": []}

# Test data for error response
ERROR_RESPONSE = {"metadata": {"status": "404"}}


@pytest.mark.asyncio
async def test_get_count_success(mocker: MockerFixture):
    """Test get_count for a successful API response."""
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = SUCCESS_COUNT_RESPONSE

    mock_get = mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    async with EdinetClient() as client:
        count = await client.get_count("2024-01-01")
        assert count == 123
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_get_count_zero(mocker: MockerFixture):
    """Test get_count when the API returns zero."""
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = ZERO_COUNT_RESPONSE

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    async with EdinetClient() as client:
        count = await client.get_count("2024-01-01")
        assert count == 0


@pytest.mark.asyncio
async def test_get_count_api_error(mocker: MockerFixture):
    """Test get_count for an API error response."""
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 404
    mock_response.json.return_value = ERROR_RESPONSE

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    async with EdinetClient() as client:
        count = await client.get_count("2024-01-01")
        assert count == 0


@pytest.mark.asyncio
async def test_get_list_success(mocker: MockerFixture):
    """Test get_list for a successful API response."""
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = SUCCESS_LIST_RESPONSE

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)
    mocker.patch("kabukit.edinet.client.clean_list", side_effect=clean_list)

    async with EdinetClient() as client:
        df = await client.get_list("2024-01-01")
        assert isinstance(df, pl.DataFrame)
        assert df.shape == (2, 4)
        assert df["docID"][0] == "S100ABC"


@pytest.mark.asyncio
async def test_get_list_zero(mocker: MockerFixture):
    """Test get_list when the API returns zero results."""
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = ZERO_LIST_RESPONSE

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    async with EdinetClient() as client:
        df = await client.get_list("2024-01-01")
        assert df.is_empty()


@pytest.mark.asyncio
async def test_get_list_api_error(mocker: MockerFixture):
    """Test get_list for an API error response."""
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 500

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    async with EdinetClient() as client:
        df = await client.get_list("2024-01-01")
        assert df.is_empty()


@pytest.mark.asyncio
async def test_get_pdf_success(mocker: MockerFixture):
    """Test get_pdf when the PDF is available."""
    # Mock response for _get_metadata
    mock_meta_response = mocker.Mock(spec=httpx.Response)
    mock_meta_response.status_code = 200
    mock_meta_response.json.return_value = SUCCESS_LIST_RESPONSE

    # Mock response for the actual PDF download
    mock_pdf_response = mocker.Mock(spec=httpx.Response)
    mock_pdf_response.status_code = 200
    mock_pdf_response.content = b"pdf_content"

    mock_get = mocker.patch(
        "httpx.AsyncClient.get", side_effect=[mock_meta_response, mock_pdf_response]
    )

    async with EdinetClient() as client:
        content = await client.get_pdf("S100ABC")
        assert content == b"pdf_content"
        assert mock_get.call_count == 2


@pytest.mark.asyncio
async def test_get_pdf_not_available(mocker: MockerFixture):
    """Test get_pdf when the PDF is not available."""
    mock_meta_response = mocker.Mock(spec=httpx.Response)
    mock_meta_response.status_code = 200
    mock_meta_response.json.return_value = SUCCESS_LIST_RESPONSE

    mocker.patch("httpx.AsyncClient.get", return_value=mock_meta_response)

    async with EdinetClient() as client:
        with pytest.raises(ValueError, match="PDF is not available"):
            await client.get_pdf("S100DEF")


@pytest.mark.asyncio
async def test_get_zip_success(mocker: MockerFixture):
    """Test get_zip when the ZIP is available."""
    mock_meta_response = mocker.Mock(spec=httpx.Response)
    mock_meta_response.status_code = 200
    mock_meta_response.json.return_value = SUCCESS_LIST_RESPONSE

    mock_zip_response = mocker.Mock(spec=httpx.Response)
    mock_zip_response.status_code = 200
    mock_zip_response.content = b"zip_content"

    mocker.patch(
        "httpx.AsyncClient.get", side_effect=[mock_meta_response, mock_zip_response]
    )

    async with EdinetClient() as client:
        content = await client.get_zip("S100ABC")
        assert content == b"zip_content"


@pytest.mark.asyncio
async def test_get_zip_not_available(mocker: MockerFixture):
    """Test get_zip when the ZIP is not available."""
    mock_meta_response = mocker.Mock(spec=httpx.Response)
    mock_meta_response.status_code = 200
    mock_meta_response.json.return_value = SUCCESS_LIST_RESPONSE

    mocker.patch("httpx.AsyncClient.get", return_value=mock_meta_response)

    async with EdinetClient() as client:
        with pytest.raises(ValueError, match="ZIP is not available"):
            await client.get_zip("S100DEF")


@pytest.mark.asyncio
async def test_get_csv_success(mocker: MockerFixture):
    """Test get_csv when the CSV is available."""
    mock_meta_response = mocker.Mock(spec=httpx.Response)
    mock_meta_response.status_code = 200
    mock_meta_response.json.return_value = SUCCESS_LIST_RESPONSE

    mock_csv_response = mocker.Mock(spec=httpx.Response)
    mock_csv_response.status_code = 200
    mock_csv_response.content = b"col1,col2\nval1,val2"

    mocker.patch(
        "httpx.AsyncClient.get", side_effect=[mock_meta_response, mock_csv_response]
    )
    mocker.patch("kabukit.edinet.client.clean_csv", side_effect=clean_csv)

    async with EdinetClient() as client:
        df = await client.get_csv("S100ABC")
        assert isinstance(df, pl.DataFrame)
        assert "docID" in df.columns


@pytest.mark.asyncio
async def test_get_csv_not_available(mocker: MockerFixture):
    """Test get_csv when the CSV is not available."""
    mock_meta_response = mocker.Mock(spec=httpx.Response)
    mock_meta_response.status_code = 200
    mock_meta_response.json.return_value = SUCCESS_LIST_RESPONSE

    mocker.patch("httpx.AsyncClient.get", return_value=mock_meta_response)

    async with EdinetClient() as client:
        with pytest.raises(ValueError, match="CSV is not available"):
            await client.get_csv("S100DEF")
