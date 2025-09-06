import io
import pathlib
import zipfile

import pytest

from kabukit.edinet.client import EdinetClient


@pytest.mark.asyncio
async def test_parse_xbrl(client: EdinetClient) -> None:
    content = await client.get_zip("S100W71P")
    zf = zipfile.ZipFile(io.BytesIO(content))

    for file_info in zf.infolist():
        if "XBRL/PublicDoc" in file_info.filename and file_info.filename.endswith(
            ".xbrl",
        ):
            with zf.open(file_info) as f:
                content = f.read()
                data = client.parse_xbrl(content)
                assert "NetSales" in data
                assert "context" in data
                assert "period" in data["context"]
                assert "consolidated" in data["context"]
